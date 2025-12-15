#!/usr/bin/env python3
"""
MP4 to MP3 Audio Extractor v2.0
Extracts high-quality audio from MP4 video files and saves as MP3

Production-ready with features:
- Progress bars and real-time status
- Parallel batch processing
- Metadata preservation (ID3 tags, artwork)
- Flexible configuration via files or CLI
- Enhanced error handling and logging
"""

import sys
import argparse
from pathlib import Path
from typing import List

# Import from our package
from mp3extractor import __version__
from mp3extractor.core import (
    check_ffmpeg,
    FFmpegNotFoundError,
    extract_audio,
    InvalidInputError,
    ConversionError,
    DiskSpaceError
)
from mp3extractor.config import Config, load_config, save_default_config
from mp3extractor.logging_config import setup_logging, log_system_info
from mp3extractor.parallel import ParallelProcessor, get_optimal_worker_count
from mp3extractor.progress import create_progress_bar, create_progress_callback
from mp3extractor.metadata import copy_metadata_if_enabled


def get_input_files(input_pattern: str) -> List[Path]:
    """
    Get list of input files from pattern, directory, or single file

    Args:
        input_pattern: File path, directory, or glob pattern

    Returns:
        List of Path objects for MP4 files
    """
    input_path = Path(input_pattern)

    # Single file
    if input_path.is_file():
        return [input_path]

    # Directory
    if input_path.is_dir():
        mp4_files = list(input_path.glob('*.mp4'))
        mp4_files.extend(input_path.glob('*.MP4'))
        mp4_files.extend(input_path.glob('*.m4v'))
        mp4_files.extend(input_path.glob('*.M4V'))
        return sorted(mp4_files)

    # Glob pattern
    if '*' in input_pattern:
        mp4_files = list(Path().glob(input_pattern))
        return sorted(mp4_files)

    # Try as single file even if doesn't exist (will error later)
    return [input_path]


def process_single_file(input_file: Path, config: Config, logger):
    """
    Process a single file

    Args:
        input_file: Input file path
        config: Configuration
        logger: Logger instance

    Returns:
        True if successful, False otherwise
    """
    try:
        # Determine output file
        if config.output_dir:
            output_dir = Path(config.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / input_file.with_suffix('.mp3').name
        else:
            output_file = input_file.with_suffix('.mp3')

        # Create progress bar
        if config.show_progress and not config.no_progress:
            progress_bar = create_progress_bar(
                desc=f"Converting {input_file.name}",
                total=100,
                position=0,
                leave=True,
                simple=config.simple_progress
            )

            with progress_bar:
                callback = create_progress_callback(progress_bar)

                success = extract_audio(
                    input_file=str(input_file),
                    output_file=str(output_file),
                    bitrate=config.bitrate,
                    sample_rate=config.sample_rate,
                    progress_callback=callback,
                    preserve_metadata=False  # Will copy separately
                )
        else:
            # No progress bar
            success = extract_audio(
                input_file=str(input_file),
                output_file=str(output_file),
                bitrate=config.bitrate,
                sample_rate=config.sample_rate,
                progress_callback=None,
                preserve_metadata=False
            )

        if success:
            # Copy metadata after conversion if enabled
            if config.preserve_metadata:
                copy_metadata_if_enabled(
                    source_file=input_file,
                    dest_file=output_file,
                    enabled=True,
                    tags_to_copy=config.metadata_tags
                )

            print(f"✓ Successfully extracted audio to {output_file}")
            return True
        else:
            print(f"✗ Failed to extract audio from {input_file.name}")
            return False

    except InvalidInputError as e:
        print(f"Error: {e}")
        logger.error(str(e))
        return False

    except ConversionError as e:
        print(f"Error: {e}")
        logger.error(str(e))
        return False

    except DiskSpaceError as e:
        print(f"Error: {e}")
        logger.error(str(e))
        return False

    except Exception as e:
        print(f"Unexpected error: {e}")
        logger.error(f"Unexpected error processing {input_file.name}", exc_info=True)
        return False


def process_batch(input_files: List[Path], config: Config, logger):
    """
    Process multiple files

    Args:
        input_files: List of input files
        config: Configuration
        logger: Logger instance
    """
    if not input_files:
        print("No MP4 files found")
        return

    print(f"Found {len(input_files)} MP4 file(s)\n")

    # Determine output directory
    output_dir = Path(config.output_dir) if config.output_dir else None
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Determine worker count
    if config.sequential or config.workers == '1':
        workers = 1
    elif config.workers == 'auto':
        workers = get_optimal_worker_count()
    else:
        workers = int(config.workers)

    # Use parallel processor
    processor = ParallelProcessor(
        workers=workers,
        bitrate=config.bitrate,
        sample_rate=config.sample_rate,
        preserve_metadata=False,  # Will handle separately
        fail_fast=config.fail_fast,
        simple_progress=config.simple_progress,
        show_progress=config.show_progress and not config.no_progress
    )

    # Process files
    results, success_count, failure_count = processor.process_files(
        input_files=input_files,
        output_dir=output_dir
    )

    # Copy metadata for successful conversions if enabled
    if config.preserve_metadata:
        print("\nCopying metadata...")
        for result in results:
            if result.success:
                if output_dir:
                    dest_file = output_dir / result.input_file.with_suffix('.mp3').name
                else:
                    dest_file = result.input_file.with_suffix('.mp3')

                copy_metadata_if_enabled(
                    source_file=result.input_file,
                    dest_file=dest_file,
                    enabled=True,
                    tags_to_copy=config.metadata_tags
                )

    # Print summary
    print(f"\n{'='*50}")
    print(f"Batch Processing Complete")
    print(f"{'='*50}")
    print(f"Total files:      {len(input_files)}")
    print(f"Successful:       {success_count}")
    print(f"Failed:           {failure_count}")
    print(f"Success rate:     {success_count / len(input_files) * 100:.1f}%")

    # List failures if any
    if failure_count > 0:
        print(f"\nFailed files:")
        for result in results:
            if not result.success:
                print(f"  - {result.input_file.name}: {result.error_message}")


def main():
    parser = argparse.ArgumentParser(
        description=f'MP4 to MP3 Audio Extractor v{__version__} - Extract high-quality MP3 audio from MP4 videos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single file
  python mp4-to-mp3-extractor.py video.mp4

  # Custom output name
  python mp4-to-mp3-extractor.py video.mp4 -o audio.mp3

  # Batch convert directory
  python mp4-to-mp3-extractor.py raw_vids/ -o mp3s/

  # Glob pattern with parallel processing
  python mp4-to-mp3-extractor.py "*.mp4" -o mp3s/ --workers 4

  # Generate default config file
  python mp4-to-mp3-extractor.py --generate-config

  # Use custom config file
  python mp4-to-mp3-extractor.py video.mp4 --config my-config.yaml

For more information, visit: https://github.com/yourusername/mp3extractor
        """
    )

    # Positional arguments
    parser.add_argument('input', nargs='?',
                       help='MP4 file, directory, or pattern (e.g., *.mp4)')

    # Output options
    parser.add_argument('-o', '--output',
                       help='Output file (single) or directory (batch)')

    # Audio quality options
    parser.add_argument('-b', '--bitrate',
                       default='320k',
                       help='Audio bitrate (default: 320k)')
    parser.add_argument('-s', '--sample-rate',
                       type=int,
                       help='Sample rate in Hz (e.g., 44100, 48000)')

    # Processing options
    parser.add_argument('-w', '--workers',
                       help='Number of parallel workers (default: auto)')
    parser.add_argument('--sequential',
                       action='store_true',
                       help='Force sequential processing')
    parser.add_argument('--fail-fast',
                       action='store_true',
                       help='Stop on first error in batch')

    # Metadata options
    parser.add_argument('--preserve-metadata',
                       action='store_true',
                       default=None,
                       help='Preserve metadata (default: enabled)')
    parser.add_argument('--no-metadata',
                       action='store_true',
                       help='Skip metadata preservation')

    # Progress options
    parser.add_argument('--no-progress',
                       action='store_true',
                       help='Disable progress bars')
    parser.add_argument('--simple-progress',
                       action='store_true',
                       help='Use simple progress (terminal compatibility)')

    # Logging options
    parser.add_argument('--log-level',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                       help='Logging level (default: INFO)')
    parser.add_argument('--log-file',
                       help='Write logs to file')
    parser.add_argument('-v', '--verbose',
                       action='store_true',
                       help='Verbose output (DEBUG level)')
    parser.add_argument('-q', '--quiet',
                       action='store_true',
                       help='Quiet mode (errors only)')

    # Config options
    parser.add_argument('--config',
                       help='Path to config file')
    parser.add_argument('--generate-config',
                       action='store_true',
                       help='Generate default config file and exit')

    # Version
    parser.add_argument('--version',
                       action='version',
                       version=f'MP3 Extractor v{__version__}')

    args = parser.parse_args()

    # Handle --generate-config
    if args.generate_config:
        try:
            config_path = save_default_config()
            print(f"Generated default config file: {config_path}")
            print("\nYou can edit this file to set your preferences.")
            print("Config file location:")
            print(f"  {config_path}")
            return 0
        except Exception as e:
            print(f"Error generating config file: {e}")
            return 1

    # Require input if not generating config
    if not args.input:
        parser.print_help()
        return 1

    # Load configuration
    try:
        config = load_config(args)

        # Override output_dir from CLI
        if args.output:
            config.output_dir = args.output

        # Handle --no-metadata
        if args.no_metadata:
            config.preserve_metadata = False

    except ValueError as e:
        print(f"Configuration error: {e}")
        return 1

    # Setup logging
    logger = setup_logging(
        log_level=config.log_level,
        log_file=config.log_file,
        verbose=config.verbose,
        quiet=config.quiet
    )

    if config.verbose:
        log_system_info()

    # Check ffmpeg
    try:
        check_ffmpeg()
    except FFmpegNotFoundError:
        print("Error: ffmpeg is not installed or not in PATH")
        print("\nTo install ffmpeg:")
        print("  - macOS:   brew install ffmpeg")
        print("  - Ubuntu:  sudo apt-get install ffmpeg")
        print("  - Windows: choco install ffmpeg  (or download from ffmpeg.org)")
        return 1

    # Get input files
    input_files = get_input_files(args.input)

    if not input_files:
        print(f"No files found matching: {args.input}")
        return 1

    # Process files
    if len(input_files) == 1 and not Path(args.input).is_dir():
        # Single file mode
        success = process_single_file(input_files[0], config, logger)
        return 0 if success else 1
    else:
        # Batch mode
        process_batch(input_files, config, logger)
        return 0


if __name__ == '__main__':
    sys.exit(main())
