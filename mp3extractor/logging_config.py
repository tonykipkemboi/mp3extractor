"""
Logging configuration and setup

Provides structured logging with custom formatters for console and file output.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler


class ColoredFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to console output
    """

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }

    def format(self, record):
        """Format log record with colors"""
        # Add color to level name
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}"
                f"{record.levelname}"
                f"{self.COLORS['RESET']}"
            )

        return super().format(record)


class PlainFormatter(logging.Formatter):
    """
    Plain text formatter for file output (no colors)
    """

    def format(self, record):
        """Format log record without colors"""
        return super().format(record)


def setup_logging(
    log_level: str = 'INFO',
    log_file: Optional[str] = None,
    verbose: bool = False,
    quiet: bool = False
) -> logging.Logger:
    """
    Setup logging configuration

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        verbose: Enable verbose output (DEBUG level)
        quiet: Suppress console output except errors

    Returns:
        Configured logger instance
    """
    # Get or create logger
    logger = logging.getLogger('mp3extractor')

    # Clear any existing handlers
    logger.handlers.clear()

    # Set level
    if verbose:
        logger.setLevel(logging.DEBUG)
    elif quiet:
        logger.setLevel(logging.ERROR)
    else:
        level = getattr(logging, log_level.upper(), logging.INFO)
        logger.setLevel(level)

    # Console handler with colors
    if not quiet:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logger.level)

        # Use colored formatter for terminal output
        console_format = '%(levelname)s: %(message)s'
        if sys.stdout.isatty():
            console_formatter = ColoredFormatter(console_format)
        else:
            console_formatter = PlainFormatter(console_format)

        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        try:
            log_path = Path(log_file).expanduser()
            log_path.parent.mkdir(parents=True, exist_ok=True)

            # Use rotating file handler (max 10MB, keep 5 backups)
            file_handler = RotatingFileHandler(
                log_path,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )

            file_handler.setLevel(logging.DEBUG)  # Always log everything to file

            # Plain formatter for file output with more details
            file_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            file_formatter = PlainFormatter(file_format, datefmt='%Y-%m-%d %H:%M:%S')

            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

            logger.debug(f"Logging to file: {log_path}")

        except Exception as e:
            # If file logging fails, log to console but don't crash
            logger.error(f"Could not setup file logging: {e}")

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def log_system_info():
    """Log system information for debugging"""
    import platform
    import os

    logger = logging.getLogger('mp3extractor')

    logger.debug("="*50)
    logger.debug("System Information")
    logger.debug("="*50)
    logger.debug(f"Platform: {platform.system()} {platform.release()}")
    logger.debug(f"Python: {platform.python_version()}")
    logger.debug(f"Working Directory: {os.getcwd()}")
    logger.debug("="*50)


def log_error_with_context(
    error: Exception,
    context: str,
    input_file: Optional[str] = None
):
    """
    Log error with additional context

    Args:
        error: Exception that occurred
        context: Description of what was being attempted
        input_file: Optional file that caused the error
    """
    logger = logging.getLogger('mp3extractor')

    error_type = type(error).__name__
    error_msg = str(error)

    logger.error(f"{context}: {error_type} - {error_msg}")

    if input_file:
        logger.error(f"  Input file: {input_file}")

    # Log traceback at debug level
    logger.debug("Exception details:", exc_info=True)


def get_default_log_file() -> Path:
    """
    Get default log file path

    Returns:
        Path to default log file in user's config directory
    """
    # Use XDG Base Directory specification
    if sys.platform == 'win32':
        config_dir = Path.home() / 'AppData' / 'Local' / 'mp3extractor'
    else:
        config_dir = Path.home() / '.config' / 'mp3extractor'

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / 'extractor.log'


def cleanup_old_logs(log_dir: Path, max_age_days: int = 30):
    """
    Clean up old log files

    Args:
        log_dir: Directory containing log files
        max_age_days: Maximum age of log files in days
    """
    import time

    logger = logging.getLogger('mp3extractor')

    if not log_dir.exists():
        return

    cutoff_time = time.time() - (max_age_days * 24 * 3600)
    removed_count = 0

    try:
        for log_file in log_dir.glob('*.log*'):
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                removed_count += 1

        if removed_count > 0:
            logger.debug(f"Cleaned up {removed_count} old log file(s)")

    except Exception as e:
        logger.warning(f"Could not clean up old logs: {e}")
