"""
Job management service
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from ..models import Job, JobFile
from ..schemas import JobStatusResponse, JobListItem, JobListResponse, FileStatusResponse


class JobService:
    """
    Service for job CRUD operations
    """

    @staticmethod
    def get_job(db: Session, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        return db.query(Job).filter(Job.id == job_id).first()

    @staticmethod
    def get_job_with_files(db: Session, job_id: str) -> Optional[JobStatusResponse]:
        """Get job with all file details"""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return None

        # Build response
        files = [
            FileStatusResponse(
                filename=f.input_filename,
                status=f.status,
                progress=f.progress,
                output_filename=f.output_filename,
                output_size=f.output_size,
                error_message=f.error_message
            )
            for f in job.files
        ]

        return JobStatusResponse(
            job_id=job.id,
            status=job.status,
            created_at=job.created_at,
            updated_at=job.updated_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            bitrate=job.bitrate,
            sample_rate=job.sample_rate,
            preserve_metadata=job.preserve_metadata,
            total_files=job.total_files,
            completed_files=job.completed_files,
            failed_files=job.failed_files,
            overall_progress=job.overall_progress,
            files=files,
            error_message=job.error_message
        )

    @staticmethod
    def list_jobs(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        status_filter: Optional[str] = None
    ) -> JobListResponse:
        """List jobs with pagination"""
        query = db.query(Job)

        # Apply status filter
        if status_filter:
            query = query.filter(Job.status == status_filter)

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        jobs = query.order_by(desc(Job.created_at)).offset(offset).limit(page_size).all()

        # Build response with full job details including files
        job_items = []
        for job in jobs:
            # Get files for this job
            files = [
                FileStatusResponse(
                    input_filename=f.input_filename,
                    output_filename=f.output_filename,
                    status=f.status,
                    progress=f.progress,
                    output_size=f.output_size,
                    error_message=f.error_message
                )
                for f in job.files
            ]

            job_items.append(JobStatusResponse(
                job_id=job.id,
                status=job.status,
                created_at=job.created_at,
                updated_at=job.updated_at,
                started_at=job.started_at,
                completed_at=job.completed_at,
                bitrate=job.bitrate,
                sample_rate=job.sample_rate,
                preserve_metadata=job.preserve_metadata,
                total_files=job.total_files,
                completed_files=job.completed_files,
                failed_files=job.failed_files,
                overall_progress=job.overall_progress,
                files=files,
                error_message=job.error_message
            ))

        return JobListResponse(
            jobs=job_items,
            total=total,
            page=page,
            page_size=page_size
        )

    @staticmethod
    def delete_job(db: Session, job_id: str) -> bool:
        """Delete job and all associated files"""
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return False

        # Delete job (cascade will delete job_files)
        db.delete(job)
        db.commit()
        return True

    @staticmethod
    def update_job_status(
        db: Session,
        job_id: str,
        status: str,
        error_message: Optional[str] = None
    ):
        """Update job status"""
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = status
            job.updated_at = datetime.utcnow()

            if status == "processing" and not job.started_at:
                job.started_at = datetime.utcnow()
            elif status in ["completed", "failed", "cancelled"]:
                job.completed_at = datetime.utcnow()

            if error_message:
                job.error_message = error_message

            db.commit()

    @staticmethod
    def update_job_progress(
        db: Session,
        job_id: str,
        completed_files: int,
        failed_files: int,
        overall_progress: float
    ):
        """Update job progress"""
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.completed_files = completed_files
            job.failed_files = failed_files
            job.overall_progress = overall_progress
            job.updated_at = datetime.utcnow()
            db.commit()

    @staticmethod
    def update_file_status(
        db: Session,
        job_id: str,
        filename: str,
        status: str,
        progress: float = 0.0,
        output_filename: Optional[str] = None,
        output_size: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        """Update individual file status"""
        job_file = db.query(JobFile).filter(
            JobFile.job_id == job_id,
            JobFile.input_filename == filename
        ).first()

        if job_file:
            job_file.status = status
            job_file.progress = progress

            if status == "processing" and not job_file.started_at:
                job_file.started_at = datetime.utcnow()
            elif status in ["completed", "failed"]:
                job_file.completed_at = datetime.utcnow()

            if output_filename:
                job_file.output_filename = output_filename
            if output_size:
                job_file.output_size = output_size
            if error_message:
                job_file.error_message = error_message

            db.commit()

    @staticmethod
    def clear_old_jobs(db: Session, days: int = 7) -> int:
        """Delete jobs older than specified days"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        old_jobs = db.query(Job).filter(Job.created_at < cutoff_date).all()
        count = len(old_jobs)

        for job in old_jobs:
            db.delete(job)

        db.commit()
        return count


# Global job service instance
job_service = JobService()
