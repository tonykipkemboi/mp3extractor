"""
Conversion service - integrates with mp3extractor package
"""

import asyncio
from pathlib import Path
from typing import Optional, Callable
from sqlalchemy.orm import Session

# Import existing mp3extractor package
from mp3extractor.core import extract_audio, InvalidInputError, ConversionError, DiskSpaceError
from mp3extractor.metadata import copy_metadata_if_enabled

from ..models import Job, JobFile
from ..services.job_service import job_service
from ..services.file_service import file_service
from ..services.progress_service import progress_service


class ConversionService:
    """
    Service for converting MP4 files to MP3

    Wraps the existing mp3extractor package with web-specific functionality
    """

    def __init__(self):
        self.active_jobs = {}  # Track active conversion jobs
        self.max_concurrent_files = 3  # Process up to 3 files in parallel

    async def convert_job(
        self,
        job_id: str,
        db: Session
    ):
        """
        Convert all files in a job

        Args:
            job_id: Job ID
            db: Database session
            progress_callback: Optional callback for progress updates
        """
        # Mark as active
        self.active_jobs[job_id] = True

        try:
            # Get job
            job = job_service.get_job(db, job_id)
            if not job:
                raise Exception(f"Job {job_id} not found")

            # Update job status to processing
            job_service.update_job_status(db, job_id, "processing")

            # Get upload and output directories
            upload_dir = file_service.get_job_upload_dir(job_id)
            output_dir = file_service.get_job_output_dir(job_id)

            # Get all job files
            files = job.files
            total_files = len(files)
            completed_count = 0
            failed_count = 0

            # Semaphore to limit concurrent file processing
            semaphore = asyncio.Semaphore(self.max_concurrent_files)

            # Track results
            results = {"completed": 0, "failed": 0}
            results_lock = asyncio.Lock()

            # Convert single file (helper function)
            async def convert_single_file(file_record):
                async with semaphore:  # Limit concurrent conversions
                    # Check if job was cancelled
                    if not self.active_jobs.get(job_id):
                        return "cancelled"

                    input_path = upload_dir / file_record.input_filename
                    output_filename = Path(file_record.input_filename).stem + ".mp3"
                    output_path = output_dir / output_filename

                    # Update file status to processing
                    job_service.update_file_status(
                        db, job_id, file_record.input_filename, "processing"
                    )

                    try:
                        # Throttle progress updates (only every 5%)
                        last_progress = [0.0]

                        # Create progress callback for this file
                        def file_progress_cb(current_ms: int, total_ms: int):
                            if total_ms > 0:
                                progress = current_ms / total_ms
                                # Only update if progress increased by at least 5%
                                if progress - last_progress[0] >= 0.05 or progress >= 0.99:
                                    last_progress[0] = progress
                                    # Update database
                                    job_service.update_file_status(
                                        db, job_id, file_record.input_filename,
                                        "processing", progress=progress
                                    )
                                    # Schedule SSE broadcast
                                    try:
                                        loop = asyncio.get_event_loop()
                                        asyncio.ensure_future(
                                            progress_service.broadcast(job_id, "file_progress", {
                                                "job_id": job_id,
                                                "filename": file_record.input_filename,
                                                "progress": progress,
                                                "current_ms": current_ms,
                                                "total_ms": total_ms
                                            }),
                                            loop=loop
                                        )
                                    except:
                                        pass

                        # Convert file using existing mp3extractor
                        await asyncio.to_thread(
                            extract_audio,
                            input_file=str(input_path),
                            output_file=str(output_path),
                            bitrate=job.bitrate,
                            sample_rate=job.sample_rate,
                            progress_callback=file_progress_cb,
                            preserve_metadata=False  # Will handle separately
                        )

                        # Copy metadata if enabled
                        if job.preserve_metadata and output_path.exists():
                            await asyncio.to_thread(
                                copy_metadata_if_enabled,
                                source_file=input_path,
                                dest_file=output_path,
                                enabled=True
                            )

                        # Get output file size
                        output_size = output_path.stat().st_size if output_path.exists() else None

                        # Mark file as completed
                        job_service.update_file_status(
                            db, job_id, file_record.input_filename,
                            "completed", progress=1.0,
                            output_filename=output_filename,
                            output_size=output_size
                        )

                        # Update results counter
                        async with results_lock:
                            results["completed"] += 1
                            completed = results["completed"]
                            failed = results["failed"]
                            overall_progress = (completed + failed) / total_files
                            job_service.update_job_progress(
                                db, job_id, completed, failed, overall_progress
                            )

                        # Send SSE event
                        await progress_service.broadcast(job_id, "file_completed", {
                            "job_id": job_id,
                            "filename": file_record.input_filename,
                            "output_filename": output_filename,
                            "output_size": output_size
                        })

                        return "completed"

                    except (InvalidInputError, ConversionError, DiskSpaceError) as e:
                        # Mark file as failed
                        job_service.update_file_status(
                            db, job_id, file_record.input_filename,
                            "failed", error_message=str(e)
                        )

                        # Update results counter
                        async with results_lock:
                            results["failed"] += 1
                            completed = results["completed"]
                            failed = results["failed"]
                            overall_progress = (completed + failed) / total_files
                            job_service.update_job_progress(
                                db, job_id, completed, failed, overall_progress
                            )

                        # Send SSE event
                        await progress_service.broadcast(job_id, "error", {
                            "job_id": job_id,
                            "filename": file_record.input_filename,
                            "error": str(e)
                        })

                        return "failed"

                    except Exception as e:
                        # Unexpected error
                        job_service.update_file_status(
                            db, job_id, file_record.input_filename,
                            "failed", error_message=f"Unexpected error: {str(e)}"
                        )

                        # Update results counter
                        async with results_lock:
                            results["failed"] += 1
                            completed = results["completed"]
                            failed = results["failed"]
                            overall_progress = (completed + failed) / total_files
                            job_service.update_job_progress(
                                db, job_id, completed, failed, overall_progress
                            )

                        await progress_service.broadcast(job_id, "error", {
                            "job_id": job_id,
                            "filename": file_record.input_filename,
                            "error": str(e)
                        })

                        return "failed"

            # Process all files in parallel (with concurrency limit)
            await asyncio.gather(*[convert_single_file(f) for f in files])

            # Get final counts
            completed_count = results["completed"]
            failed_count = results["failed"]

            # Mark job as completed or failed
            if failed_count == total_files:
                job_service.update_job_status(db, job_id, "failed", "All files failed")
            elif failed_count > 0:
                job_service.update_job_status(db, job_id, "completed", f"{failed_count} file(s) failed")
            else:
                job_service.update_job_status(db, job_id, "completed")

            # Send job completed event
            await progress_service.broadcast(job_id, "job_completed", {
                "job_id": job_id,
                "total_files": total_files,
                "completed_files": completed_count,
                "failed_files": failed_count
            })

        except Exception as e:
            # Fatal error
            job_service.update_job_status(db, job_id, "failed", str(e))
            await progress_service.broadcast(job_id, "error", {
                "job_id": job_id,
                "error": str(e)
            })

        finally:
            # Remove from active jobs
            if job_id in self.active_jobs:
                del self.active_jobs[job_id]

    async def cancel_job(self, job_id: str, db: Session) -> bool:
        """
        Cancel an active conversion job

        Args:
            job_id: Job ID
            db: Database session

        Returns:
            True if cancelled, False if not found or not active
        """
        if job_id not in self.active_jobs:
            return False

        # Mark as cancelled (the conversion loop will check this)
        self.active_jobs[job_id] = False
        job_service.update_job_status(db, job_id, "cancelled")
        return True

    def is_job_active(self, job_id: str) -> bool:
        """Check if a job is currently being processed"""
        return job_id in self.active_jobs


# Global conversion service instance
conversion_service = ConversionService()
