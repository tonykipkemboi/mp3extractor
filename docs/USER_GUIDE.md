# User Guide

Complete guide to using the MP3 Extractor Web UI.

## Table of Contents

- [Getting Started](#getting-started)
- [Uploading Files](#uploading-files)
- [Configuring Settings](#configuring-settings)
- [Converting Files](#converting-files)
- [Downloading Results](#downloading-results)
- [Job History](#job-history)
- [Tips & Best Practices](#tips--best-practices)

## Getting Started

### Starting the Application

1. Open your terminal
2. Navigate to the project directory (or use `mp3dev` alias)
3. Start the servers:
```bash
./dev.sh
```

4. Open your browser to http://localhost:3000

### Interface Overview

The application has two main pages:

1. **Home Page** (`/`) - Upload and convert files
2. **History Page** (`/history`) - View past conversions

## Uploading Files

### Drag and Drop

1. Drag MP4 file(s) from your computer
2. Drop them onto the upload zone
3. Files will appear in the "Selected Files" list

### Click to Browse

1. Click anywhere in the upload zone
2. Select one or multiple MP4 files
3. Click "Open"

### Supported Formats

- **Video**: MP4 files only
- **Multiple Files**: Yes, upload as many as you need
- **File Size**: Up to 500MB per file (configurable)

### Removing Files

- Click the **X** button next to any file to remove it before conversion
- Click **Clear Files** button to remove all selected files

## Configuring Settings

Before starting conversion, configure the audio quality settings in the right panel.

### Quality Presets

Quick presets for common use cases:

| Preset | Bitrate | Best For | File Size |
|--------|---------|----------|-----------|
| **Low (128k)** | 128 kbps | Podcasts, audiobooks | Smallest |
| **Medium (192k)** | 192 kbps | General listening | Small |
| **High (256k)** | 256 kbps | High quality music | Medium |
| **Custom (320k)** | 320 kbps | Maximum quality | Largest |

### Manual Configuration

#### Bitrate
- **Range**: 128k - 320k
- **Higher = Better Quality** but larger file size
- **Recommended**: 320k for music, 192k for speech

#### Sample Rate
- **Auto (Original)**: Keep the video's sample rate (recommended)
- **44.1 kHz (CD Quality)**: Standard for music
- **48 kHz (Professional)**: Studio quality

#### Preserve Metadata
- **Enabled**: Copy title, artist, album, artwork from video
- **Disabled**: Create clean MP3 without metadata
- **Recommended**: Keep enabled

## Converting Files

### Start Conversion

1. Upload your MP4 file(s)
2. Configure quality settings (or use a preset)
3. Click the **Start Conversion** button

### Real-time Progress

During conversion, you'll see:

#### Overall Progress Card
- **Overall Progress**: Total percentage complete
- **Completed**: Number of files successfully converted (green)
- **Processing**: Files currently being converted (blue, animated)
- **Failed**: Files that encountered errors (red)
- **Success Rate**: Percentage of successful conversions

#### Individual File Progress
Each file shows:
- **File name**: Original MP4 filename
- **Status badge**: pending, processing, completed, or failed
- **Progress bar**: Real-time conversion progress (when processing)
- **Download button**: Appears when completed

### Processing Time

Conversion speed depends on:
- **File size**: Larger files take longer
- **Settings**: Higher quality = longer conversion
- **Parallel Processing**: Up to 3 files convert simultaneously
- **Hardware**: Your computer's CPU speed

**Typical Times:**
- 100MB video: ~30-60 seconds
- 500MB video: 2-4 minutes
- 1GB video: 4-8 minutes

## Downloading Results

### Download Individual Files

1. Click the **Download** button (down arrow icon) next to completed files
2. File downloads as `{original-name}.mp3`

### Download All Files

1. After all files complete, click **Download All (ZIP)**
2. Downloads a ZIP file containing all converted MP3s
3. ZIP file named: `mp3_conversion_{job_id}.zip`

### File Locations

Downloaded files are saved to your browser's default download folder:
- **macOS**: `~/Downloads/`
- **Windows**: `C:\Users\{YourName}\Downloads\`
- **Linux**: `~/Downloads/`

## Job History

Access at http://localhost:3000/history

### Viewing Past Jobs

The history page shows all your conversion jobs with:
- **Status badge**: Current job status
- **Date**: When the job was created (relative time)
- **Filenames**: Original video filenames (up to 2 shown)
- **Files count**: Completed / Total files
- **Quality settings**: Bitrate, sample rate, metadata preservation

### Job Actions

#### Refresh
Click the **Refresh** button to update the job list.

#### Download Completed Jobs
Click **Download** button to re-download files from completed jobs.

#### Delete Jobs
1. Click the **trash icon** next to a job
2. Confirm deletion in the dialog
3. Job and all associated files are permanently deleted

### Job Statuses

| Status | Description |
|--------|-------------|
| **Queued** | Job created, waiting to start |
| **Processing** | Currently converting files |
| **Completed** | All files converted successfully |
| **Completed with errors** | Some files failed |
| **Failed** | Job failed to complete |
| **Cancelled** | Job was cancelled by user |

### Automatic Cleanup

Old jobs are automatically cleaned up after 7 days to save disk space. You can manually delete jobs anytime.

## Tips & Best Practices

### For Best Results

1. **Use 320k bitrate** for music you care about
2. **Keep metadata enabled** to preserve song information
3. **Use original sample rate** unless you have a specific need
4. **Upload multiple files** to take advantage of parallel processing

### Optimizing Speed

1. **Batch process**: Upload all files at once for faster overall completion
2. **Lower quality**: Use 192k or 256k if file size matters more than quality
3. **Close other programs**: Free up CPU for faster conversion

### Avoiding Errors

1. **Check file format**: Only MP4 files are supported
2. **Verify file integrity**: Corrupted videos will fail
3. **Check disk space**: Ensure enough space for converted files
4. **Don't close browser**: Keep the page open during conversion

### Managing Storage

1. **Download promptly**: Files are deleted after 7 days
2. **Delete old jobs**: Use history page to clear completed jobs
3. **Monitor disk usage**: Large batches require significant storage

### Quality vs File Size

**320k MP3 from 100MB MP4:**
- Output size: ~8-10MB
- Quality: Excellent (indistinguishable from original)

**192k MP3 from 100MB MP4:**
- Output size: ~5-6MB
- Quality: Good (suitable for most uses)

**128k MP3 from 100MB MP4:**
- Output size: ~3-4MB
- Quality: Acceptable (noticeable compression)

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + Click` | Select upload zone |
| `Esc` | Close dialogs |

## Troubleshooting

### Upload Issues

**Problem**: Can't upload files
- Check file format (must be MP4)
- Check file size (max 500MB)
- Try refreshing the page

**Problem**: Files disappear after upload
- Don't navigate away during upload
- Check browser console for errors

### Conversion Issues

**Problem**: Conversion fails immediately
- Check ffmpeg is installed
- Verify file is not corrupted
- Check backend logs: `tail -f backend.log`

**Problem**: Conversion stuck at 0%
- Wait a moment, progress may be delayed
- Check backend is running: http://localhost:8000/api/health
- Refresh the page and try again

**Problem**: Some files succeed, others fail
- Failed files are likely corrupted or invalid
- Try converting failed files individually
- Check error message in the UI

### Download Issues

**Problem**: Download button doesn't appear
- Wait for conversion to complete
- Refresh the page
- Check job in history page

**Problem**: Downloaded file won't play
- Verify file is not 0 bytes
- Try a different media player
- Reconvert the file with different settings

### Performance Issues

**Problem**: Conversion is very slow
- Close other resource-intensive programs
- Try lower quality settings
- Process fewer files at once
- Check CPU usage in system monitor

## Getting Help

If you encounter issues:

1. Check the backend logs: `tail -f backend.log`
2. Check the frontend logs: `tail -f frontend.log`
3. Verify services are running: http://localhost:8000/api/health
4. Review the [Setup Guide](SETUP.md) for configuration issues
5. Check the [API Documentation](API.md) for technical details

## Advanced Usage

### Custom Settings

For specific requirements:
- **Voice recordings**: 128k, mono, preserve metadata off
- **Music archiving**: 320k, 48kHz, preserve metadata on
- **Podcast editing**: 192k, 44.1kHz, preserve metadata on
- **Quick preview**: 128k, auto sample rate, metadata off

### Bulk Operations

For large batch conversions:
1. Upload all files at once (parallel processing)
2. Use medium quality (192k) for faster processing
3. Download as ZIP when complete
4. Delete job immediately to free storage

### Re-downloading

If you lose downloaded files:
1. Go to History page
2. Find your job (jobs kept for 7 days)
3. Click Download button to get files again
