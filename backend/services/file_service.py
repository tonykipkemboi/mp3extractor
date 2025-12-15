"""
File storage and management service
"""

import os
import shutil
import zipfile
from pathlib import Path
from typing import List, Optional
import uuid
import aiofiles
from fastapi import UploadFile


class FileService:
    """
    Manages file storage for uploads and outputs
    """

    def __init__(self, storage_path: str = "./storage"):
        self.storage_path = Path(storage_path)
        self.uploads_dir = self.storage_path / "uploads"
        self.outputs_dir = self.storage_path / "outputs"
        self.temp_dir = self.storage_path / "temp"

        # Create directories if they don't exist
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def get_job_upload_dir(self, job_id: str) -> Path:
        """Get upload directory for a job"""
        job_dir = self.uploads_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_dir

    def get_job_output_dir(self, job_id: str) -> Path:
        """Get output directory for a job"""
        job_dir = self.outputs_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_dir

    async def save_upload(
        self,
        file: UploadFile,
        job_id: str
    ) -> tuple[Path, int]:
        """
        Save uploaded file to storage

        Args:
            file: Uploaded file
            job_id: Job ID

        Returns:
            Tuple of (file_path, file_size)
        """
        upload_dir = self.get_job_upload_dir(job_id)
        file_path = upload_dir / file.filename

        # Save file
        file_size = 0
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(8192):  # 8KB chunks
                await f.write(chunk)
                file_size += len(chunk)

        return file_path, file_size

    async def save_multiple_uploads(
        self,
        files: List[UploadFile],
        job_id: str
    ) -> List[tuple[str, Path, int]]:
        """
        Save multiple uploaded files

        Args:
            files: List of uploaded files
            job_id: Job ID

        Returns:
            List of tuples (filename, file_path, file_size)
        """
        results = []
        for file in files:
            file_path, file_size = await self.save_upload(file, job_id)
            results.append((file.filename, file_path, file_size))

        return results

    def get_output_file_path(self, job_id: str, filename: str) -> Optional[Path]:
        """
        Get path to output file

        Args:
            job_id: Job ID
            filename: Output filename

        Returns:
            Path to file if exists, None otherwise
        """
        output_dir = self.get_job_output_dir(job_id)
        file_path = output_dir / filename

        if file_path.exists():
            return file_path
        return None

    def create_zip_archive(self, job_id: str, output_filename: str = "converted.zip") -> Optional[Path]:
        """
        Create ZIP archive of all output files for a job

        Args:
            job_id: Job ID
            output_filename: Name of ZIP file

        Returns:
            Path to ZIP file if successful, None otherwise
        """
        output_dir = self.get_job_output_dir(job_id)
        zip_path = self.temp_dir / f"{job_id}_{output_filename}"

        # Get all MP3 files in output directory
        mp3_files = list(output_dir.glob("*.mp3"))

        if not mp3_files:
            return None

        # Create ZIP file
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for mp3_file in mp3_files:
                # Add file with just the filename (no directory structure)
                zipf.write(mp3_file, arcname=mp3_file.name)

        return zip_path

    def cleanup_job_files(self, job_id: str) -> bool:
        """
        Delete all files associated with a job

        Args:
            job_id: Job ID

        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete upload directory
            upload_dir = self.uploads_dir / job_id
            if upload_dir.exists():
                shutil.rmtree(upload_dir)

            # Delete output directory
            output_dir = self.outputs_dir / job_id
            if output_dir.exists():
                shutil.rmtree(output_dir)

            # Delete temp ZIP files for this job
            for temp_file in self.temp_dir.glob(f"{job_id}_*"):
                temp_file.unlink()

            return True
        except Exception as e:
            print(f"Error cleaning up job {job_id}: {e}")
            return False

    def get_job_disk_usage(self, job_id: str) -> dict:
        """
        Get disk usage for a job

        Args:
            job_id: Job ID

        Returns:
            Dictionary with upload_size, output_size, total_size in bytes
        """
        upload_dir = self.uploads_dir / job_id
        output_dir = self.outputs_dir / job_id

        upload_size = sum(f.stat().st_size for f in upload_dir.rglob("*") if f.is_file()) if upload_dir.exists() else 0
        output_size = sum(f.stat().st_size for f in output_dir.rglob("*") if f.is_file()) if output_dir.exists() else 0

        return {
            "upload_size": upload_size,
            "output_size": output_size,
            "total_size": upload_size + output_size
        }

    def validate_upload_file(self, filename: str) -> tuple[bool, Optional[str]]:
        """
        Validate uploaded file

        Args:
            filename: Filename to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file extension
        allowed_extensions = {'.mp4', '.m4v', '.mov', '.avi', '.mkv'}
        file_ext = Path(filename).suffix.lower()

        if file_ext not in allowed_extensions:
            return False, f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"

        # Check for directory traversal
        if '..' in filename or filename.startswith('/'):
            return False, "Invalid filename"

        return True, None

    def cleanup_old_temp_files(self, max_age_hours: int = 24):
        """
        Clean up old temporary files

        Args:
            max_age_hours: Maximum age of temp files in hours
        """
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        for temp_file in self.temp_dir.iterdir():
            if temp_file.is_file():
                file_age = current_time - temp_file.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        temp_file.unlink()
                    except Exception as e:
                        print(f"Error deleting temp file {temp_file}: {e}")


# Global file service instance
file_service = FileService()
