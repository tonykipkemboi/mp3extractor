"""
Core audio extraction functionality

This module contains the main conversion logic, FFmpeg wrapper,
and validation functions.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Callable, List, Tuple
import logging

logger = logging.getLogger('mp3extractor')


# Custom exceptions for better error handling
class FFmpegNotFoundError(Exception):
    """Raised when ffmpeg is not found in PATH"""
    pass


class InvalidInputError(Exception):
    """Raised when input file is invalid or not found"""
    pass


class ConversionError(Exception):
    """Raised when audio conversion fails"""
    pass


class DiskSpaceError(Exception):
    """Raised when insufficient disk space is available"""
    pass


def check_ffmpeg() -> bool:
    """
    Check if ffmpeg is installed and accessible

    Returns:
        bool: True if ffmpeg is available, False otherwise

    Raises:
        FFmpegNotFoundError: If ffmpeg is not found in PATH
    """
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            check=True,
            timeout=5
        )
        version_line = result.stdout.decode().split('\n')[0]
        logger.debug(f"Found {version_line}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.error(f"ffmpeg check failed: {e}")
        raise FFmpegNotFoundError("ffmpeg is not installed or not in PATH")


def validate_input(input_file: Path) -> Tuple[bool, Optional[str]]:
    """
    Validate input file exists and has audio stream

    Args:
        input_file: Path to input MP4 file

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not input_file.exists():
        return False, f"File not found: {input_file}"

    if not input_file.is_file():
        return False, f"Not a file: {input_file}"

    if input_file.suffix.lower() not in ['.mp4', '.m4v', '.mov', '.avi', '.mkv']:
        logger.warning(f"Unexpected file extension: {input_file.suffix}")

    # Check if file has audio stream using ffprobe
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'a:0',
             '-show_entries', 'stream=codec_type', '-of', 'default=nw=1',
             str(input_file)],
            capture_output=True,
            text=True,
            timeout=10
        )

        if 'codec_type=audio' not in result.stdout:
            return False, f"No audio stream found in: {input_file.name}"

    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        # If ffprobe fails, log but continue (file might still work)
        logger.warning(f"Could not verify audio stream in {input_file.name}")

    return True, None


def get_audio_duration(input_file: Path) -> Optional[float]:
    """
    Get audio duration in seconds using ffprobe

    Args:
        input_file: Path to input file

    Returns:
        Duration in seconds, or None if unable to determine
    """
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', str(input_file)],
            capture_output=True,
            text=True,
            timeout=10
        )

        duration = float(result.stdout.strip())
        logger.debug(f"Audio duration: {duration:.2f}s")
        return duration

    except (ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        logger.warning(f"Could not determine audio duration: {e}")
        return None


def check_disk_space(output_path: Path, estimated_size: int) -> bool:
    """
    Check if sufficient disk space is available

    Args:
        output_path: Path where output file will be written
        estimated_size: Estimated output file size in bytes

    Returns:
        bool: True if sufficient space available
    """
    try:
        stat = os.statvfs(output_path.parent)
        free_space = stat.f_bavail * stat.f_frsize

        # Add 10% buffer
        required_space = estimated_size * 1.1

        if free_space < required_space:
            logger.error(f"Insufficient disk space: {free_space / 1024**2:.1f}MB available, "
                        f"{required_space / 1024**2:.1f}MB required")
            return False

        return True

    except Exception as e:
        logger.warning(f"Could not check disk space: {e}")
        # If we can't check, assume it's fine
        return True


def extract_audio(
    input_file: str,
    output_file: Optional[str] = None,
    bitrate: str = '320k',
    sample_rate: Optional[int] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    preserve_metadata: bool = True
) -> bool:
    """
    Extract audio from video file and save as MP3

    Args:
        input_file: Path to input video file
        output_file: Path to output MP3 file (optional, auto-generated if None)
        bitrate: Audio bitrate (e.g., '320k', '256k')
        sample_rate: Sample rate in Hz (optional)
        progress_callback: Optional callback function(current_ms, total_ms) for progress updates
        preserve_metadata: Whether to preserve metadata (requires metadata module)

    Returns:
        bool: True if successful, False otherwise

    Raises:
        InvalidInputError: If input file is invalid
        ConversionError: If conversion fails
        DiskSpaceError: If insufficient disk space
    """
    input_path = Path(input_file)

    # Validate input
    is_valid, error_msg = validate_input(input_path)
    if not is_valid:
        logger.error(error_msg)
        raise InvalidInputError(error_msg)

    # Generate output filename if not provided
    if output_file is None:
        output_file = input_path.with_suffix('.mp3')
    else:
        output_file = Path(output_file)

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Get duration for progress tracking
    duration = get_audio_duration(input_path)
    duration_ms = int(duration * 1000) if duration else None

    # Estimate output size (bitrate * duration)
    if duration:
        # bitrate in kb/s, duration in seconds, convert to bytes
        bitrate_num = int(bitrate.rstrip('k'))
        estimated_size = (bitrate_num * 1000 * duration) // 8

        if not check_disk_space(output_file, estimated_size):
            raise DiskSpaceError(f"Insufficient disk space for output file")

    # Build ffmpeg command
    cmd = [
        'ffmpeg',
        '-i', str(input_path),
        '-vn',  # No video
        '-acodec', 'libmp3lame',  # MP3 codec
        '-b:a', bitrate,  # Audio bitrate
        '-q:a', '0',  # Highest quality VBR
    ]

    # Add sample rate if specified
    if sample_rate:
        cmd.extend(['-ar', str(sample_rate)])

    # Add progress reporting if callback provided
    if progress_callback:
        cmd.extend(['-progress', 'pipe:1', '-stats_period', '0.5'])

    # Add metadata preservation flag
    if preserve_metadata:
        cmd.extend(['-map_metadata', '0'])

    # Add output file and overwrite flag
    cmd.extend(['-y', str(output_file)])

    logger.info(f"Extracting audio: {input_path.name} -> {output_file.name}")
    logger.debug(f"Command: {' '.join(cmd)}")

    try:
        # Run ffmpeg with progress monitoring if callback provided
        if progress_callback and duration_ms:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Parse progress from stdout
            for line in process.stdout:
                line = line.strip()
                if line.startswith('out_time_ms='):
                    try:
                        current_ms = int(line.split('=')[1])
                        progress_callback(current_ms, duration_ms)
                    except (ValueError, IndexError):
                        pass

            # Wait for process to complete
            process.wait()

            if process.returncode != 0:
                stderr = process.stderr.read()
                logger.error(f"FFmpeg error: {stderr}")
                raise ConversionError(f"Conversion failed for {input_path.name}")

        else:
            # Run without progress monitoring
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout for large files
            )

            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise ConversionError(f"Conversion failed for {input_path.name}")

        # Verify output file was created
        if not output_file.exists():
            raise ConversionError(f"Output file was not created: {output_file}")

        output_size = output_file.stat().st_size
        logger.info(f"Successfully extracted audio: {output_file.name} ({output_size / 1024**2:.1f}MB)")

        return True

    except subprocess.TimeoutExpired:
        logger.error(f"Conversion timeout for {input_path.name}")
        raise ConversionError(f"Conversion timed out for {input_path.name}")

    except Exception as e:
        logger.error(f"Unexpected error during conversion: {e}", exc_info=True)
        raise ConversionError(f"Conversion failed: {e}")


class FFmpegWrapper:
    """
    Wrapper class for ffmpeg operations

    Provides a cleaner interface for audio extraction with
    built-in error handling and logging.
    """

    def __init__(
        self,
        bitrate: str = '320k',
        sample_rate: Optional[int] = None,
        preserve_metadata: bool = True
    ):
        """
        Initialize FFmpeg wrapper

        Args:
            bitrate: Default audio bitrate
            sample_rate: Default sample rate
            preserve_metadata: Whether to preserve metadata by default
        """
        self.bitrate = bitrate
        self.sample_rate = sample_rate
        self.preserve_metadata = preserve_metadata

        # Check ffmpeg availability
        try:
            check_ffmpeg()
        except FFmpegNotFoundError:
            logger.critical("FFmpeg not found - cannot proceed")
            raise

    def convert(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> bool:
        """
        Convert video file to MP3

        Args:
            input_file: Path to input video file
            output_file: Path to output MP3 file (optional)
            progress_callback: Optional progress callback

        Returns:
            bool: True if successful
        """
        return extract_audio(
            input_file=input_file,
            output_file=output_file,
            bitrate=self.bitrate,
            sample_rate=self.sample_rate,
            progress_callback=progress_callback,
            preserve_metadata=self.preserve_metadata
        )

    def batch_convert(
        self,
        input_files: List[Path],
        output_dir: Optional[Path] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Tuple[int, int]:
        """
        Convert multiple files sequentially

        Args:
            input_files: List of input file paths
            output_dir: Output directory (optional)
            progress_callback: Optional callback(current, total, filename)

        Returns:
            Tuple of (success_count, total_count)
        """
        success_count = 0
        total = len(input_files)

        for i, input_file in enumerate(input_files, 1):
            try:
                if output_dir:
                    output_file = output_dir / input_file.with_suffix('.mp3').name
                else:
                    output_file = None

                if progress_callback:
                    progress_callback(i, total, input_file.name)

                if self.convert(str(input_file), str(output_file) if output_file else None):
                    success_count += 1

            except (InvalidInputError, ConversionError, DiskSpaceError) as e:
                logger.error(f"Failed to convert {input_file.name}: {e}")
                # Continue with next file
                continue

        return success_count, total
