"""
MP3 Extractor - Production-ready MP4 to MP3 audio extraction tool

This package provides high-quality audio extraction from MP4 video files
with features including:
- Progress bars and real-time status
- Parallel batch processing
- Metadata preservation (ID3 tags, artwork)
- Flexible configuration via files or CLI
- Enhanced error handling and logging
"""

__version__ = '2.0.0'
__author__ = 'MP3 Extractor Contributors'

# Public API exports
from .core import (
    FFmpegWrapper,
    check_ffmpeg,
    extract_audio,
    validate_input,
)

__all__ = [
    'FFmpegWrapper',
    'check_ffmpeg',
    'extract_audio',
    'validate_input',
    '__version__',
]
