## MP4 → MP3 Audio Extractor v2.0

Extract high-quality MP3 audio from MP4 videos using ffmpeg. Production-ready with progress bars, parallel processing, metadata preservation, and flexible configuration options.

### Terminal Output Example

![Terminal screenshot placeholder](docs/terminal-screenshot.png)

---

## What's New in v2.0

- ✅ **Real-time progress bars** - See conversion progress with percentage, speed, and ETA
- ✅ **Parallel processing** - Process multiple files simultaneously (3-5x faster)
- ✅ **Metadata preservation** - Automatically copy ID3 tags and artwork from source
- ✅ **Configuration files** - Set defaults via YAML/JSON config files
- ✅ **Enhanced logging** - Structured logging with file output and log levels
- ✅ **Better error handling** - Detailed error messages and graceful degradation
- ✅ **Modular architecture** - Clean, maintainable codebase

## Features

### Core Capabilities
- **High quality MP3**: LAME encoder (`libmp3lame`) with `-q:a 0` and configurable bitrate (default `320k`)
- **Flexible input**: Single file, directory, or glob pattern support
- **Customizable output**: Choose output file name or output directory
- **Cross-platform**: macOS, Linux, and Windows (with ffmpeg installed)

### Production Features
- **Progress tracking**: Real-time progress bars with tqdm (or simple fallback)
- **Parallel batch processing**: Auto-detects CPU cores, configurable worker count
- **Metadata support**: Preserves title, artist, album, artwork (using mutagen or ffmpeg)
- **Config files**: Hierarchical configuration (user → project → CLI)
- **Structured logging**: Color-coded console output, optional file logging
- **Error recovery**: Continue processing on failures, detailed error reporting

---

## Prerequisites

- **Python**: 3.8+ (standard library + 1 required dependency)
- **ffmpeg**: Required and must be on your PATH

### Install ffmpeg

**macOS (Homebrew)**:
```bash
brew update && brew install ffmpeg
```

**Ubuntu/Debian**:
```bash
sudo apt update && sudo apt install -y ffmpeg
```

**Windows (Chocolatey)**:
```powershell
choco install ffmpeg
```

**Windows (Scoop)**:
```powershell
scoop install ffmpeg
```

### Install Python Dependencies

```bash
# Install required and optional dependencies
pip install -r requirements.txt

# Or install manually:
pip install tqdm                    # Required - progress bars
pip install PyYAML mutagen         # Optional - config files & metadata
```

**Dependencies:**
- `tqdm` (required) - Progress bars
- `PyYAML` (optional) - YAML config file support (JSON fallback available)
- `mutagen` (optional) - Full metadata/artwork support (ffmpeg fallback available)

---

## Quick Start

### Basic Usage

```bash
# Single file
python3 mp4-to-mp3-extractor.py video.mp4

# Custom output name
python3 mp4-to-mp3-extractor.py video.mp4 -o audio.mp3

# Batch convert directory
python3 mp4-to-mp3-extractor.py raw_vids/ -o mp3s/

# Glob pattern (quote in zsh)
python3 mp4-to-mp3-extractor.py "raw_vids/*.mp4" -o mp3s/
```

### With New Features

```bash
# Parallel processing with 4 workers
python3 mp4-to-mp3-extractor.py raw_vids/ -o mp3s/ --workers 4

# Custom bitrate without progress bars
python3 mp4-to-mp3-extractor.py video.mp4 -b 256k --no-progress

# Verbose logging to file
python3 mp4-to-mp3-extractor.py raw_vids/ -o mp3s/ --verbose --log-file convert.log

# Skip metadata preservation
python3 mp4-to-mp3-extractor.py video.mp4 --no-metadata

# Generate default config file
python3 mp4-to-mp3-extractor.py --generate-config
```

### Make Script Executable (Optional)

```bash
chmod +x mp4-to-mp3-extractor.py
./mp4-to-mp3-extractor.py raw_vids -o mp3s
```

---

## Command Reference

### Basic Options

| Option | Description | Example |
|--------|-------------|---------|
| `input` | MP4 file, directory, or pattern | `video.mp4`, `raw_vids/`, `"*.mp4"` |
| `-o, --output` | Output file or directory | `-o mp3s/` |
| `-b, --bitrate` | Audio bitrate (default: 320k) | `-b 256k` |
| `-s, --sample-rate` | Sample rate in Hz | `-s 48000` |

### Processing Options

| Option | Description | Default |
|--------|-------------|---------|
| `-w, --workers` | Number of parallel workers | `auto` |
| `--sequential` | Force sequential processing | `false` |
| `--fail-fast` | Stop on first error | `false` |

### Metadata Options

| Option | Description | Default |
|--------|-------------|---------|
| `--preserve-metadata` | Preserve metadata | `true` |
| `--no-metadata` | Skip metadata preservation | `false` |

### Progress Options

| Option | Description | Default |
|--------|-------------|---------|
| `--no-progress` | Disable progress bars | `false` |
| `--simple-progress` | Use simple progress (compatibility) | `false` |

### Logging Options

| Option | Description | Default |
|--------|-------------|---------|
| `--log-level` | Set log level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `--log-file` | Write logs to file | (none) |
| `-v, --verbose` | Enable verbose output (DEBUG) | `false` |
| `-q, --quiet` | Quiet mode (errors only) | `false` |

### Configuration Options

| Option | Description |
|--------|-------------|
| `--config` | Path to config file |
| `--generate-config` | Generate default config file |
| `--version` | Show version number |

---

## Configuration Files

### Creating a Config File

```bash
# Generate default config
python3 mp4-to-mp3-extractor.py --generate-config

# Edit the generated file
nano ~/.config/mp3extractor/config.yaml
```

### Config File Locations

The tool loads configuration in this order (later overrides earlier):

1. **Default values** - Built-in defaults
2. **User config** - `~/.config/mp3extractor/config.yaml`
3. **Project config** - `./.mp3extractor.yaml` (current directory)
4. **CLI arguments** - Command-line flags (highest priority)

### Example Config File

```yaml
# MP3 Extractor Configuration

# Audio settings
bitrate: 320k
sample_rate: 48000

# Output settings
output_dir: ./mp3s

# Processing settings
workers: 4              # or 'auto'
fail_fast: false

# Metadata settings
preserve_metadata: true
metadata_tags:
  - title
  - artist
  - album
  - artwork

# Progress settings
show_progress: true
simple_progress: false

# Logging settings
log_level: INFO
log_file: ~/.config/mp3extractor/extractor.log
```

Both YAML and JSON formats are supported. Use `.yaml`, `.yml`, or `.json` file extensions.

---

## Advanced Examples

### Parallel Processing

```bash
# Auto-detect optimal worker count (default)
python3 mp4-to-mp3-extractor.py raw_vids/ -o mp3s/

# Specific worker count
python3 mp4-to-mp3-extractor.py raw_vids/ -o mp3s/ --workers 4

# Sequential processing (useful for debugging)
python3 mp4-to-mp3-extractor.py raw_vids/ -o mp3s/ --sequential
```

### Custom Audio Quality

```bash
# Lower bitrate for smaller files
python3 mp4-to-mp3-extractor.py video.mp4 -b 128k

# High bitrate with specific sample rate
python3 mp4-to-mp3-extractor.py video.mp4 -b 320k -s 48000
```

### Logging and Debugging

```bash
# Verbose output to console
python3 mp4-to-mp3-extractor.py raw_vids/ -o mp3s/ --verbose

# Log to file for troubleshooting
python3 mp4-to-mp3-extractor.py raw_vids/ -o mp3s/ --log-file convert.log --log-level DEBUG

# Quiet mode (only show errors)
python3 mp4-to-mp3-extractor.py raw_vids/ -o mp3s/ --quiet
```

### Using Config Files

```bash
# Create project-specific config
cat > .mp3extractor.yaml << EOF
bitrate: 256k
workers: 2
preserve_metadata: true
log_level: INFO
EOF

# Run with project config
python3 mp4-to-mp3-extractor.py raw_vids/ -o mp3s/

# Override config with CLI args
python3 mp4-to-mp3-extractor.py raw_vids/ -o mp3s/ -b 320k --workers 4
```

---

## How It Works

### FFmpeg Command

The tool wraps ffmpeg with optimized settings:

```bash
ffmpeg -i input.mp4 \
  -vn \                      # No video
  -acodec libmp3lame \       # MP3 LAME encoder
  -b:a 320k \                # Bitrate
  -q:a 0 \                   # Highest VBR quality
  -map_metadata 0 \          # Copy metadata
  -progress pipe:1 \         # Progress reporting
  output.mp3
```

### Parallel Processing

- Auto-detects CPU cores and uses `n-1` workers by default
- Uses Python's `multiprocessing.Pool` for true parallelism
- Each worker processes files independently with its own progress bar
- Main process coordinates overall batch progress
- Graceful error handling - continues on individual failures

### Metadata Preservation

**With mutagen (full support):**
- Copies ID3 tags: title, artist, album, date, genre
- Preserves artwork/cover images (JPEG/PNG)
- Writes ID3v2.4 tags to MP3

**With ffmpeg fallback (basic):**
- Copies basic text metadata using `-map_metadata`
- Limited artwork support
- Automatic fallback if mutagen not installed

---

## Project Structure

```text
mp3extractor/
├── mp4-to-mp3-extractor.py      # Main CLI script
├── mp3extractor/                 # Package modules
│   ├── __init__.py
│   ├── core.py                   # Core conversion logic
│   ├── config.py                 # Configuration management
│   ├── progress.py               # Progress bars
│   ├── parallel.py               # Parallel processing
│   ├── metadata.py               # Metadata handling
│   └── logging_config.py         # Logging setup
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── docs/                         # Documentation assets
├── raw_vids/                     # Input videos (gitignored)
└── mp3s/                         # Output MP3s (gitignored)
```

---

## Troubleshooting

### Common Issues

**ffmpeg not found**
- Ensure ffmpeg is installed: `ffmpeg -version`
- Check PATH: `which ffmpeg` (Unix) or `where ffmpeg` (Windows)
- See installation instructions above

**No MP4 files found**
- For glob patterns in zsh, wrap in quotes: `"*.mp4"`
- Check file extensions (case-sensitive on Unix)
- Use absolute paths if relative paths fail

**Permission denied**
- Make script executable: `chmod +x mp4-to-mp3-extractor.py`
- Check write permissions for output directory
- Run with appropriate user permissions

**Progress bars not showing**
- Install tqdm: `pip install tqdm`
- Use `--simple-progress` for terminal compatibility
- Disable with `--no-progress` if issues persist

**Metadata not preserved**
- Install mutagen for full support: `pip install mutagen`
- Basic metadata preserved via ffmpeg fallback
- Artwork requires mutagen - ffmpeg fallback doesn't support it
- Check source file has metadata: `ffprobe -v quiet -show_format video.mp4`

**Parallel processing issues**
- Reduce workers: `--workers 2`
- Force sequential: `--sequential`
- Check system resources (CPU, memory)
- Enable verbose logging: `--verbose --log-file debug.log`

### Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `FFmpegNotFoundError` | ffmpeg not installed | Install ffmpeg (see Prerequisites) |
| `InvalidInputError` | File not found or no audio | Check file path and format |
| `ConversionError` | FFmpeg conversion failed | Check ffmpeg stderr in log file |
| `DiskSpaceError` | Insufficient disk space | Free up space or change output location |

### Getting Help

- Enable verbose logging: `--verbose --log-file debug.log`
- Check log file for detailed error messages
- Verify ffmpeg works: `ffmpeg -i video.mp4 -vn -acodec libmp3lame test.mp3`
- Test with single file before batch processing
- Use `--sequential` to isolate parallel processing issues

---

## Performance Tips

- **Parallel processing**: Use `--workers` equal to your CPU cores - 1
- **Large batches**: Automatic worker management handles 100+ files efficiently
- **Progress overhead**: Minimal (~1-2%), disable with `--no-progress` if needed
- **Metadata**: Mutagen is faster than ffmpeg for metadata operations
- **Disk I/O**: Use SSD for input/output if processing many files
- **Memory**: Each worker uses ~50-100MB; adjust workers if memory-constrained

---

## Development

### Running from Source

```bash
# Clone or download the repository
cd mp3extractor

# Install dependencies
pip install -r requirements.txt

# Run directly
python3 mp4-to-mp3-extractor.py --help
```

### Project Dependencies

- **Required**: `tqdm>=4.65.0`
- **Optional**: `PyYAML>=6.0.1`, `mutagen>=1.47.0`
- **System**: `ffmpeg` (latest version recommended)

---

## Notes

- **Backward compatibility**: All v1.0 commands work unchanged in v2.0
- **Config precedence**: CLI arguments > project config > user config > defaults
- **Output paths**: Directory for batch, file path for single file
- **Metadata**: Enabled by default, disable with `--no-metadata`
- **Progress bars**: Enabled by default, disable with `--no-progress`
- **Workers**: Auto-detected by default, configure with `--workers N`

---

## License

This project is provided as-is for personal and commercial use.

---

## Contributing

Contributions welcome! Please ensure:
- Code follows existing style
- All features have appropriate error handling
- Backward compatibility is maintained
- Documentation is updated

---

Happy extracting! 🎧
