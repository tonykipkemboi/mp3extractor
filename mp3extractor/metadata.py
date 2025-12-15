"""
Metadata preservation for audio files

Handles copying of ID3 tags and artwork from source video to output MP3.
Supports both mutagen (full featured) and ffmpeg (basic) backends.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any, List
import subprocess
import logging

logger = logging.getLogger('mp3extractor')

# Try to import mutagen
try:
    from mutagen.mp4 import MP4
    from mutagen.id3 import ID3, ID3NoHeaderError, TIT2, TPE1, TPE2, TALB, TDRC, TCON, APIC
    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False
    logger.debug("mutagen not available, will use ffmpeg for metadata")


class MetadataHandler(ABC):
    """
    Abstract base class for metadata handlers
    """

    @abstractmethod
    def extract_metadata(self, source_file: Path) -> Dict[str, Any]:
        """
        Extract metadata from source file

        Args:
            source_file: Path to source video file

        Returns:
            Dictionary of metadata tags
        """
        pass

    @abstractmethod
    def write_metadata(self, dest_file: Path, metadata: Dict[str, Any]) -> bool:
        """
        Write metadata to destination file

        Args:
            dest_file: Path to destination MP3 file
            metadata: Dictionary of metadata to write

        Returns:
            True if successful, False otherwise
        """
        pass

    def copy_metadata(self, source_file: Path, dest_file: Path) -> bool:
        """
        Copy metadata from source to destination

        Args:
            source_file: Path to source video file
            dest_file: Path to destination MP3 file

        Returns:
            True if successful, False otherwise
        """
        try:
            metadata = self.extract_metadata(source_file)
            if metadata:
                return self.write_metadata(dest_file, metadata)
            return True
        except Exception as e:
            logger.warning(f"Could not copy metadata: {e}")
            return False


class MutagenMetadataHandler(MetadataHandler):
    """
    Full-featured metadata handler using mutagen library

    Supports all common ID3 tags and artwork/cover images.
    """

    def __init__(self, tags_to_copy: Optional[List[str]] = None):
        """
        Initialize mutagen handler

        Args:
            tags_to_copy: List of tag names to copy (None for all)
        """
        if not HAS_MUTAGEN:
            raise RuntimeError("mutagen not available")

        self.tags_to_copy = tags_to_copy or ['title', 'artist', 'album', 'date', 'genre', 'artwork']

    def extract_metadata(self, source_file: Path) -> Dict[str, Any]:
        """
        Extract metadata from MP4/M4V file

        Args:
            source_file: Path to source video file

        Returns:
            Dictionary with extracted metadata
        """
        metadata = {}

        try:
            video = MP4(str(source_file))

            # Extract text tags
            tag_mapping = {
                'title': '©nam',
                'artist': '©ART',
                'album_artist': 'aART',
                'album': '©alb',
                'date': '©day',
                'genre': '©gen',
                'comment': '©cmt',
            }

            for tag_name, mp4_key in tag_mapping.items():
                if tag_name in self.tags_to_copy and mp4_key in video:
                    value = video[mp4_key]
                    if isinstance(value, list) and value:
                        metadata[tag_name] = str(value[0])
                    else:
                        metadata[tag_name] = str(value)

            # Extract artwork
            if 'artwork' in self.tags_to_copy and 'covr' in video:
                artwork_data = video['covr']
                if artwork_data:
                    # Get first artwork image
                    metadata['artwork'] = bytes(artwork_data[0])
                    logger.debug(f"Extracted artwork: {len(metadata['artwork'])} bytes")

            if metadata:
                logger.debug(f"Extracted metadata from {source_file.name}: {list(metadata.keys())}")

        except Exception as e:
            logger.warning(f"Could not extract metadata from {source_file.name}: {e}")

        return metadata

    def write_metadata(self, dest_file: Path, metadata: Dict[str, Any]) -> bool:
        """
        Write metadata to MP3 file using ID3 tags

        Args:
            dest_file: Path to MP3 file
            metadata: Dictionary of metadata

        Returns:
            True if successful
        """
        if not metadata:
            return True

        try:
            # Try to load existing ID3 tags, or create new
            try:
                tags = ID3(str(dest_file))
            except ID3NoHeaderError:
                tags = ID3()

            # Write text tags
            if 'title' in metadata:
                tags.add(TIT2(encoding=3, text=metadata['title']))

            if 'artist' in metadata:
                tags.add(TPE1(encoding=3, text=metadata['artist']))

            if 'album_artist' in metadata:
                tags.add(TPE2(encoding=3, text=metadata['album_artist']))

            if 'album' in metadata:
                tags.add(TALB(encoding=3, text=metadata['album']))

            if 'date' in metadata:
                tags.add(TDRC(encoding=3, text=metadata['date']))

            if 'genre' in metadata:
                tags.add(TCON(encoding=3, text=metadata['genre']))

            # Write artwork
            if 'artwork' in metadata:
                artwork_data = metadata['artwork']

                # Detect image type
                if artwork_data.startswith(b'\xff\xd8'):
                    mime = 'image/jpeg'
                elif artwork_data.startswith(b'\x89PNG'):
                    mime = 'image/png'
                else:
                    mime = 'image/jpeg'  # Default to JPEG

                tags.add(APIC(
                    encoding=3,
                    mime=mime,
                    type=3,  # Cover (front)
                    desc='Cover',
                    data=artwork_data
                ))

                logger.debug(f"Added artwork to {dest_file.name} ({len(artwork_data)} bytes)")

            # Save ID3 tags to file
            tags.save(str(dest_file), v2_version=4)

            logger.info(f"Wrote metadata to {dest_file.name}")
            return True

        except Exception as e:
            logger.warning(f"Could not write metadata to {dest_file.name}: {e}")
            return False


class FFmpegMetadataHandler(MetadataHandler):
    """
    Basic metadata handler using ffmpeg

    Limited to basic text metadata only (no artwork support).
    Used as fallback when mutagen is not available.
    """

    def __init__(self, tags_to_copy: Optional[List[str]] = None):
        """
        Initialize ffmpeg handler

        Args:
            tags_to_copy: List of tag names to copy (None for all)
        """
        self.tags_to_copy = tags_to_copy or ['title', 'artist', 'album', 'date']
        logger.info("Using ffmpeg for metadata (limited support, no artwork)")

    def extract_metadata(self, source_file: Path) -> Dict[str, Any]:
        """
        Extract metadata using ffprobe

        Args:
            source_file: Path to source video file

        Returns:
            Dictionary with extracted metadata
        """
        metadata = {}

        try:
            # Use ffprobe to extract metadata
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                str(source_file)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)

                # Extract tags from format section
                if 'format' in data and 'tags' in data['format']:
                    tags = data['format']['tags']

                    # Map ffmpeg tag names to our format
                    tag_mapping = {
                        'title': 'title',
                        'artist': 'artist',
                        'album': 'album',
                        'date': 'date',
                        'year': 'date',
                        'genre': 'genre',
                    }

                    for our_name, ffmpeg_name in tag_mapping.items():
                        if our_name in self.tags_to_copy:
                            # Try exact match first
                            value = tags.get(ffmpeg_name)

                            # Try case-insensitive match
                            if not value:
                                for key in tags:
                                    if key.lower() == ffmpeg_name.lower():
                                        value = tags[key]
                                        break

                            if value:
                                metadata[our_name] = str(value)

                if metadata:
                    logger.debug(f"Extracted metadata from {source_file.name}: {list(metadata.keys())}")

        except Exception as e:
            logger.warning(f"Could not extract metadata from {source_file.name}: {e}")

        return metadata

    def write_metadata(self, dest_file: Path, metadata: Dict[str, Any]) -> bool:
        """
        Write metadata to MP3 using ffmpeg

        Note: This actually requires re-encoding, so we don't do it here.
        Instead, metadata is written during conversion via -map_metadata flag.

        Args:
            dest_file: Path to MP3 file
            metadata: Dictionary of metadata

        Returns:
            True (metadata is written during conversion)
        """
        # FFmpeg metadata is written during conversion using -map_metadata
        # This method is a no-op for compatibility
        logger.debug("FFmpeg metadata written during conversion")
        return True


def create_metadata_handler(
    backend: str = 'auto',
    tags_to_copy: Optional[List[str]] = None
) -> Optional[MetadataHandler]:
    """
    Factory function to create appropriate metadata handler

    Args:
        backend: Backend to use ('auto', 'mutagen', 'ffmpeg', 'none')
        tags_to_copy: List of tags to copy

    Returns:
        MetadataHandler instance or None if disabled
    """
    if backend == 'none':
        return None

    if backend == 'mutagen':
        if not HAS_MUTAGEN:
            logger.warning("mutagen not available, falling back to ffmpeg")
            return FFmpegMetadataHandler(tags_to_copy)
        return MutagenMetadataHandler(tags_to_copy)

    if backend == 'ffmpeg':
        return FFmpegMetadataHandler(tags_to_copy)

    if backend == 'auto':
        # Try mutagen first, fall back to ffmpeg
        if HAS_MUTAGEN:
            return MutagenMetadataHandler(tags_to_copy)
        else:
            return FFmpegMetadataHandler(tags_to_copy)

    raise ValueError(f"Invalid metadata backend: {backend}")


def copy_metadata_if_enabled(
    source_file: Path,
    dest_file: Path,
    enabled: bool = True,
    tags_to_copy: Optional[List[str]] = None
) -> bool:
    """
    Convenience function to copy metadata if enabled

    Args:
        source_file: Source video file
        dest_file: Destination MP3 file
        enabled: Whether to copy metadata
        tags_to_copy: List of tags to copy

    Returns:
        True if successful or disabled, False on error
    """
    if not enabled:
        logger.debug("Metadata preservation disabled")
        return True

    if not dest_file.exists():
        logger.warning(f"Destination file does not exist: {dest_file}")
        return False

    try:
        handler = create_metadata_handler(tags_to_copy=tags_to_copy)
        if handler:
            return handler.copy_metadata(source_file, dest_file)
        return True

    except Exception as e:
        logger.warning(f"Metadata copy failed: {e}")
        return False
