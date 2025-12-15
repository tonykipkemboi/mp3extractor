"""
Parallel processing for batch conversions

Handles multiprocessing worker pool management and progress coordination.
"""

import os
import multiprocessing as mp
from multiprocessing import Pool, cpu_count
from pathlib import Path
from typing import List, Optional, Tuple, Callable
from dataclasses import dataclass
import logging

from .progress import create_progress_bar, create_progress_callback

logger = logging.getLogger('mp3extractor')


@dataclass
class ConversionTask:
    """
    Represents a single file conversion task
    """
    input_file: Path
    output_file: Optional[Path]
    bitrate: str
    sample_rate: Optional[int]
    preserve_metadata: bool


@dataclass
class ConversionResult:
    """
    Result of a conversion task
    """
    input_file: Path
    success: bool
    error_message: Optional[str] = None
    output_size: Optional[int] = None


def _worker_process_file(task: ConversionTask, position: int, simple_progress: bool) -> ConversionResult:
    """
    Worker function to process a single file

    This function runs in a separate process.

    Args:
        task: ConversionTask to process
        position: Progress bar position
        simple_progress: Use simple progress bars

    Returns:
        ConversionResult
    """
    # Import here to avoid issues with multiprocessing
    from .core import extract_audio, InvalidInputError, ConversionError, DiskSpaceError

    try:
        # Create progress bar for this file
        progress_bar = create_progress_bar(
            desc=task.input_file.name[:40],  # Truncate long names
            total=100,
            position=position,
            leave=False,
            simple=simple_progress
        )

        with progress_bar:
            # Create progress callback
            callback = create_progress_callback(progress_bar)

            # Perform conversion
            success = extract_audio(
                input_file=str(task.input_file),
                output_file=str(task.output_file) if task.output_file else None,
                bitrate=task.bitrate,
                sample_rate=task.sample_rate,
                progress_callback=callback,
                preserve_metadata=task.preserve_metadata
            )

            if success and task.output_file and task.output_file.exists():
                output_size = task.output_file.stat().st_size
                return ConversionResult(
                    input_file=task.input_file,
                    success=True,
                    output_size=output_size
                )
            else:
                return ConversionResult(
                    input_file=task.input_file,
                    success=False,
                    error_message="Conversion returned False"
                )

    except (InvalidInputError, ConversionError, DiskSpaceError) as e:
        logger.error(f"Failed to convert {task.input_file.name}: {e}")
        return ConversionResult(
            input_file=task.input_file,
            success=False,
            error_message=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error converting {task.input_file.name}: {e}", exc_info=True)
        return ConversionResult(
            input_file=task.input_file,
            success=False,
            error_message=f"Unexpected error: {e}"
        )


class ParallelProcessor:
    """
    Manages parallel batch conversion of multiple files
    """

    def __init__(
        self,
        workers: int = None,
        bitrate: str = '320k',
        sample_rate: Optional[int] = None,
        preserve_metadata: bool = True,
        fail_fast: bool = False,
        simple_progress: bool = False,
        show_progress: bool = True
    ):
        """
        Initialize parallel processor

        Args:
            workers: Number of worker processes (None for auto-detect)
            bitrate: Audio bitrate
            sample_rate: Sample rate
            preserve_metadata: Whether to preserve metadata
            fail_fast: Stop on first error
            simple_progress: Use simple progress bars
            show_progress: Show progress bars
        """
        # Determine worker count
        if workers is None or workers <= 0:
            # Auto-detect: use CPU count - 1 (leave one core free)
            self.workers = max(1, cpu_count() - 1)
        else:
            self.workers = min(workers, cpu_count())  # Don't exceed CPU count

        self.bitrate = bitrate
        self.sample_rate = sample_rate
        self.preserve_metadata = preserve_metadata
        self.fail_fast = fail_fast
        self.simple_progress = simple_progress
        self.show_progress = show_progress

        logger.info(f"Initialized parallel processor with {self.workers} workers")

    def process_files(
        self,
        input_files: List[Path],
        output_dir: Optional[Path] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Tuple[List[ConversionResult], int, int]:
        """
        Process multiple files in parallel

        Args:
            input_files: List of input file paths
            output_dir: Output directory (optional)
            progress_callback: Optional callback(completed, total)

        Returns:
            Tuple of (results, success_count, failure_count)
        """
        if not input_files:
            logger.warning("No files to process")
            return [], 0, 0

        # Create output directory if specified
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)

        # Build task list
        tasks = []
        for input_file in input_files:
            if output_dir:
                output_file = output_dir / input_file.with_suffix('.mp3').name
            else:
                output_file = input_file.with_suffix('.mp3')

            task = ConversionTask(
                input_file=input_file,
                output_file=output_file,
                bitrate=self.bitrate,
                sample_rate=self.sample_rate,
                preserve_metadata=self.preserve_metadata
            )
            tasks.append(task)

        logger.info(f"Processing {len(tasks)} file(s) with {self.workers} worker(s)")

        # For single worker, use sequential processing (simpler)
        if self.workers == 1:
            return self._process_sequential(tasks, progress_callback)

        # Use multiprocessing for parallel execution
        return self._process_parallel(tasks, progress_callback)

    def _process_sequential(
        self,
        tasks: List[ConversionTask],
        progress_callback: Optional[Callable[[int, int], None]]
    ) -> Tuple[List[ConversionResult], int, int]:
        """
        Process files sequentially (single worker)

        Args:
            tasks: List of conversion tasks
            progress_callback: Optional progress callback

        Returns:
            Tuple of (results, success_count, failure_count)
        """
        results = []
        success_count = 0
        total = len(tasks)

        # Create main progress bar
        main_bar = create_progress_bar(
            desc="Converting",
            total=total,
            position=0,
            leave=True,
            simple=self.simple_progress,
            disable=not self.show_progress
        )

        with main_bar:
            for i, task in enumerate(tasks, 1):
                # Process file
                result = _worker_process_file(task, position=1, simple_progress=self.simple_progress)

                results.append(result)

                if result.success:
                    success_count += 1
                elif self.fail_fast:
                    logger.error(f"Stopping due to error (fail-fast mode)")
                    break

                # Update progress
                main_bar.update(i, total)

                if progress_callback:
                    progress_callback(i, total)

        failure_count = total - success_count
        return results, success_count, failure_count

    def _process_parallel(
        self,
        tasks: List[ConversionTask],
        progress_callback: Optional[Callable[[int, int], None]]
    ) -> Tuple[List[ConversionResult], int, int]:
        """
        Process files in parallel using multiprocessing

        Args:
            tasks: List of conversion tasks
            progress_callback: Optional progress callback

        Returns:
            Tuple of (results, success_count, failure_count)
        """
        results = []
        success_count = 0
        total = len(tasks)
        completed = 0

        # Create main progress bar
        main_bar = create_progress_bar(
            desc="Overall Progress",
            total=total,
            position=0,
            leave=True,
            simple=self.simple_progress,
            disable=not self.show_progress
        )

        try:
            # Create worker pool
            with Pool(processes=self.workers) as pool:
                with main_bar:
                    # Submit all tasks
                    async_results = []
                    for i, task in enumerate(tasks):
                        # Position 1 onwards for per-file progress bars
                        position = (i % self.workers) + 1

                        async_result = pool.apply_async(
                            _worker_process_file,
                            args=(task, position, self.simple_progress)
                        )
                        async_results.append((task, async_result))

                    # Collect results as they complete
                    for task, async_result in async_results:
                        try:
                            result = async_result.get(timeout=3600)  # 1 hour timeout per file
                            results.append(result)

                            if result.success:
                                success_count += 1
                            elif self.fail_fast:
                                logger.error(f"Stopping due to error (fail-fast mode)")
                                pool.terminate()
                                break

                            # Update progress
                            completed += 1
                            main_bar.update(completed, total)

                            if progress_callback:
                                progress_callback(completed, total)

                        except mp.TimeoutError:
                            logger.error(f"Timeout processing {task.input_file.name}")
                            results.append(ConversionResult(
                                input_file=task.input_file,
                                success=False,
                                error_message="Processing timeout"
                            ))
                            completed += 1

                        except Exception as e:
                            logger.error(f"Error collecting result for {task.input_file.name}: {e}")
                            results.append(ConversionResult(
                                input_file=task.input_file,
                                success=False,
                                error_message=f"Result collection error: {e}"
                            ))
                            completed += 1

        except Exception as e:
            logger.error(f"Error in parallel processing: {e}", exc_info=True)

        failure_count = len(results) - success_count
        return results, success_count, failure_count


def get_optimal_worker_count() -> int:
    """
    Determine optimal number of workers for this system

    Returns:
        Recommended worker count
    """
    cpu_cores = cpu_count()

    # Leave one core free for system
    optimal = max(1, cpu_cores - 1)

    logger.debug(f"CPU cores: {cpu_cores}, optimal workers: {optimal}")

    return optimal
