"""
Job management API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..schemas import JobStatusResponse, JobListResponse
from ..services.job_service import job_service
from ..services.file_service import file_service

router = APIRouter()


@router.get("/jobs", response_model=JobListResponse, tags=["Jobs"])
async def list_jobs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """
    List all jobs with pagination

    Args:
        page: Page number (starting from 1)
        page_size: Number of items per page (1-100)
        status: Optional status filter (queued, processing, completed, failed, cancelled)

    Returns:
        Paginated list of jobs
    """
    return job_service.list_jobs(db, page=page, page_size=page_size, status_filter=status)


@router.get("/jobs/{job_id}", response_model=JobStatusResponse, tags=["Jobs"])
async def get_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed status of a specific job

    Args:
        job_id: Job ID

    Returns:
        Complete job status with all files
    """
    job = job_service.get_job_with_files(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.delete("/jobs/{job_id}", tags=["Jobs"])
async def delete_job(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a job and all associated files

    Args:
        job_id: Job ID

    Returns:
        Success message
    """
    # Delete from database
    success = job_service.delete_job(db, job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")

    # Cleanup files
    file_service.cleanup_job_files(job_id)

    return {"message": "Job deleted successfully", "job_id": job_id}


@router.post("/jobs/clear-history", tags=["Jobs"])
async def clear_old_jobs(
    days: int = Query(7, ge=1, le=365, description="Delete jobs older than N days"),
    db: Session = Depends(get_db)
):
    """
    Clear old jobs from history

    Args:
        days: Delete jobs older than this many days

    Returns:
        Number of jobs deleted
    """
    count = job_service.clear_old_jobs(db, days=days)

    return {
        "message": f"Deleted {count} old job(s)",
        "count": count,
        "days": days
    }
