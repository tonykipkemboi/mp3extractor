"""
Progress bar implementations

Provides progress tracking for audio conversion using tqdm.
Includes fallback for when tqdm is not available.
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable
import logging
import sys

logger = logging.getLogger('mp3extractor')

# Try to import tqdm
try:
    from tqdm import tqdm as _tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    logger.warning("tqdm not available, progress bars disabled")


class ProgressBar(ABC):
    """
    Abstract base class for progress bars
    """

    @abstractmethod
    def update(self, current: int, total: int):
        """
        Update progress

        Args:
            current: Current progress value
            total: Total value for 100% completion
        """
        pass

    @abstractmethod
    def close(self):
        """Clean up progress bar"""
        pass

    @abstractmethod
    def __enter__(self):
        """Context manager entry"""
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        pass


class TqdmProgressBar(ProgressBar):
    """
    Progress bar implementation using tqdm
    """

    def __init__(
        self,
        desc: str = "Converting",
        total: Optional[int] = None,
        unit: str = 'it',
        position: int = 0,
        leave: bool = True,
        disable: bool = False
    ):
        """
        Initialize tqdm progress bar

        Args:
            desc: Description text
            total: Total iterations
            unit: Unit name
            position: Bar position (for multiple bars)
            leave: Leave bar after completion
            disable: Disable progress bar
        """
        if not HAS_TQDM:
            raise RuntimeError("tqdm not available")

        self.desc = desc
        self.total = total
        self.unit = unit
        self.position = position
        self.leave = leave
        self.disable = disable
        self.pbar = None
        self._last_n = 0

    def __enter__(self):
        """Start progress bar"""
        self.pbar = _tqdm(
            desc=self.desc,
            total=self.total,
            unit=self.unit,
            position=self.position,
            leave=self.leave,
            disable=self.disable,
            file=sys.stdout,
            dynamic_ncols=True
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close progress bar"""
        self.close()

    def update(self, current: int, total: int):
        """
        Update progress bar

        Args:
            current: Current progress in milliseconds
            total: Total duration in milliseconds
        """
        if self.pbar is None:
            return

        # Update total if needed
        if self.pbar.total != total:
            self.pbar.total = total

        # Calculate progress delta
        percentage = (current / total * 100) if total > 0 else 0
        n = min(int(percentage), 100)

        # Update by delta
        delta = n - self._last_n
        if delta > 0:
            self.pbar.update(delta)
            self._last_n = n

    def set_description(self, desc: str):
        """Update description text"""
        if self.pbar:
            self.pbar.set_description(desc)

    def close(self):
        """Close and cleanup progress bar"""
        if self.pbar:
            if self._last_n < 100:
                # Ensure we reach 100%
                self.pbar.update(100 - self._last_n)
            self.pbar.close()
            self.pbar = None


class SimpleProgressBar(ProgressBar):
    """
    Simple text-based progress bar for terminals without ANSI support
    """

    def __init__(
        self,
        desc: str = "Converting",
        total: Optional[int] = None,
        position: int = 0
    ):
        """
        Initialize simple progress bar

        Args:
            desc: Description text
            total: Total value
            position: Position (ignored, for API compatibility)
        """
        self.desc = desc
        self.total = total
        self.position = position
        self._last_percentage = -1
        self._started = False

    def __enter__(self):
        """Start progress tracking"""
        self._started = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Finish progress tracking"""
        self.close()

    def update(self, current: int, total: int):
        """
        Update progress (prints every 10%)

        Args:
            current: Current progress
            total: Total value
        """
        if not self._started:
            return

        percentage = int((current / total * 100)) if total > 0 else 0
        percentage = min(percentage, 100)

        # Only print at 10% intervals
        if percentage >= self._last_percentage + 10:
            print(f"{self.desc}: {percentage}%", flush=True)
            self._last_percentage = percentage

    def close(self):
        """Finish progress"""
        if self._started and self._last_percentage < 100:
            print(f"{self.desc}: 100%", flush=True)
        self._started = False


class NoOpProgressBar(ProgressBar):
    """
    No-op progress bar (does nothing)

    Used when progress bars are disabled.
    """

    def __init__(self, *args, **kwargs):
        """Initialize (no-op)"""
        pass

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        pass

    def update(self, current: int, total: int):
        """Update (no-op)"""
        pass

    def close(self):
        """Close (no-op)"""
        pass


def create_progress_bar(
    desc: str = "Converting",
    total: Optional[int] = None,
    position: int = 0,
    leave: bool = True,
    simple: bool = False,
    disable: bool = False
) -> ProgressBar:
    """
    Factory function to create appropriate progress bar

    Args:
        desc: Description text
        total: Total iterations
        position: Bar position
        leave: Leave bar after completion
        simple: Force simple progress bar
        disable: Disable progress bar completely

    Returns:
        ProgressBar instance (Tqdm, Simple, or NoOp)
    """
    if disable:
        return NoOpProgressBar()

    if simple or not HAS_TQDM:
        return SimpleProgressBar(desc=desc, total=total, position=position)

    try:
        return TqdmProgressBar(
            desc=desc,
            total=total,
            position=position,
            leave=leave,
            disable=disable
        )
    except Exception as e:
        logger.warning(f"Could not create tqdm progress bar: {e}")
        return SimpleProgressBar(desc=desc, total=total, position=position)


def create_progress_callback(progress_bar: ProgressBar) -> Callable[[int, int], None]:
    """
    Create progress callback function for FFmpeg wrapper

    Args:
        progress_bar: ProgressBar instance

    Returns:
        Callback function(current_ms, total_ms)
    """
    def callback(current_ms: int, total_ms: int):
        """Progress callback for FFmpeg"""
        progress_bar.update(current_ms, total_ms)

    return callback


class MultiFileProgressManager:
    """
    Manages multiple progress bars for parallel processing

    Coordinates a main progress bar (overall batch) and multiple
    per-file progress bars (individual conversions).
    """

    def __init__(
        self,
        total_files: int,
        max_workers: int = 4,
        simple: bool = False,
        disable: bool = False
    ):
        """
        Initialize progress manager

        Args:
            total_files: Total number of files to process
            max_workers: Maximum number of concurrent workers
            simple: Use simple progress bars
            disable: Disable all progress bars
        """
        self.total_files = total_files
        self.max_workers = max_workers
        self.simple = simple
        self.disable = disable

        # Main progress bar (position 0)
        self.main_bar = create_progress_bar(
            desc="Overall Progress",
            total=total_files,
            position=0,
            leave=True,
            simple=simple,
            disable=disable
        )

        # Per-file progress bars (positions 1-N)
        self.file_bars = {}
        self._next_position = 1
        self._completed_count = 0

    def __enter__(self):
        """Start progress tracking"""
        self.main_bar.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop progress tracking"""
        # Close all file bars
        for bar in list(self.file_bars.values()):
            bar.close()
        self.file_bars.clear()

        # Close main bar
        self.main_bar.__exit__(exc_type, exc_val, exc_tb)

    def create_file_progress(self, file_name: str) -> ProgressBar:
        """
        Create progress bar for a file

        Args:
            file_name: Name of file being processed

        Returns:
            ProgressBar instance for this file
        """
        # Clean up completed bars to free positions
        self._cleanup_completed_bars()

        # Allocate position
        position = self._next_position
        self._next_position += 1

        # Create bar
        bar = create_progress_bar(
            desc=file_name,
            total=100,  # Percentage-based
            position=position,
            leave=False,  # Don't leave file bars after completion
            simple=self.simple,
            disable=self.disable
        )

        self.file_bars[file_name] = bar
        bar.__enter__()

        return bar

    def update_main_progress(self, increment: int = 1):
        """
        Update main progress bar

        Args:
            increment: Number of files completed
        """
        self._completed_count += increment
        self.main_bar.update(self._completed_count, self.total_files)

    def _cleanup_completed_bars(self):
        """Remove completed progress bars to free up positions"""
        # In practice, bars are removed when files complete
        # This is a placeholder for future optimization
        pass

    def complete_file(self, file_name: str):
        """
        Mark file as complete and clean up its progress bar

        Args:
            file_name: Name of completed file
        """
        if file_name in self.file_bars:
            bar = self.file_bars[file_name]
            bar.close()
            del self.file_bars[file_name]

        self.update_main_progress(1)
