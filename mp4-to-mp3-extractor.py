#!/usr/bin/env python3
"""
MP4 to MP3 Audio Extractor
Extracts high-quality audio from MP4 video files and saves as MP3
"""

import os
import sys
import subprocess
from pathlib import Path
import argparse

def check_ffmpeg():
    """Check if ffmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def extract_audio(input_file, output_file=None, bitrate='320k', sample_rate=None):
    """
    Extract audio from MP4 and save as MP3
    
    Args:
        input_file: Path to input MP4 file
        output_file: Path to output MP3 file (optional)
        bitrate: Audio bitrate (default: 320k for high quality)
        sample_rate: Sample rate in Hz (optional, e.g., 44100, 48000)
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"Error: File '{input_file}' not found")
        return False
    
    # Generate output filename if not provided
    if output_file is None:
        output_file = input_path.with_suffix('.mp3')
    else:
        output_file = Path(output_file)
    
    # Build ffmpeg command
    cmd = [
        'ffmpeg',
        '-i', str(input_path),  # Input file
        '-vn',  # No video
        '-acodec', 'libmp3lame',  # MP3 codec
        '-b:a', bitrate,  # Audio bitrate
        '-q:a', '0',  # Highest quality VBR
    ]
    
    # Add sample rate if specified
    if sample_rate:
        cmd.extend(['-ar', str(sample_rate)])
    
    # Add output file and overwrite flag
    cmd.extend(['-y', str(output_file)])
    
    print(f"Extracting audio from: {input_path.name}")
    print(f"Output: {output_file.name}")
    print(f"Bitrate: {bitrate}")
    
    try:
        # Run ffmpeg
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✓ Successfully extracted audio to {output_file.name}\n")
            return True
        else:
            print(f"Error extracting audio: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def batch_extract(input_pattern, output_dir=None, bitrate='320k', sample_rate=None):
    """
    Extract audio from multiple MP4 files
    
    Args:
        input_pattern: File pattern or directory containing MP4 files
        output_dir: Directory for output files (optional)
        bitrate: Audio bitrate
        sample_rate: Sample rate in Hz
    """
    input_path = Path(input_pattern)
    
    # Get list of MP4 files
    if input_path.is_dir():
        mp4_files = list(input_path.glob('*.mp4'))
    elif '*' in str(input_pattern):
        mp4_files = list(Path().glob(input_pattern))
    else:
        mp4_files = [input_path] if input_path.suffix == '.mp4' else []
    
    if not mp4_files:
        print("No MP4 files found")
        return
    
    print(f"Found {len(mp4_files)} MP4 file(s)\n")
    
    # Create output directory if specified
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
    
    success_count = 0
    for mp4_file in mp4_files:
        if output_dir:
            output_file = output_path / mp4_file.with_suffix('.mp3').name
        else:
            output_file = None
        
        if extract_audio(mp4_file, output_file, bitrate, sample_rate):
            success_count += 1
    
    print(f"\nCompleted: {success_count}/{len(mp4_files)} files processed successfully")

def main():
    parser = argparse.ArgumentParser(
        description='Extract high-quality MP3 audio from MP4 videos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract from single file
  python mp4_to_mp3.py video.mp4
  
  # Extract with custom output name
  python mp4_to_mp3.py video.mp4 -o audio.mp3
  
  # Extract from all MP4 files in current directory
  python mp4_to_mp3.py *.mp4
  
  # Extract from directory with custom bitrate
  python mp4_to_mp3.py /path/to/videos -b 256k
  
  # Extract with specific sample rate
  python mp4_to_mp3.py video.mp4 -s 48000
        """
    )
    
    parser.add_argument('input', 
                       help='MP4 file, directory, or pattern (e.g., *.mp4)')
    parser.add_argument('-o', '--output', 
                       help='Output file or directory')
    parser.add_argument('-b', '--bitrate', 
                       default='320k',
                       help='Audio bitrate (default: 320k for high quality)')
    parser.add_argument('-s', '--sample-rate', 
                       type=int,
                       help='Sample rate in Hz (e.g., 44100, 48000)')
    
    args = parser.parse_args()
    
    # Check if ffmpeg is installed
    if not check_ffmpeg():
        print("Error: ffmpeg is not installed or not in PATH")
        print("\nTo install ffmpeg:")
        print("  - Windows: Download from https://ffmpeg.org/download.html")
        print("  - Mac: brew install ffmpeg")
        print("  - Linux: sudo apt-get install ffmpeg (Ubuntu/Debian)")
        sys.exit(1)
    
    # Process based on input type
    input_path = Path(args.input)
    
    if '*' in args.input or input_path.is_dir():
        # Batch processing
        batch_extract(args.input, args.output, args.bitrate, args.sample_rate)
    else:
        # Single file
        extract_audio(args.input, args.output, args.bitrate, args.sample_rate)

if __name__ == '__main__':
    main()