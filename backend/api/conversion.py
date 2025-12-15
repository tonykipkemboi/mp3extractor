"""
Conversion API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import StartConversionRequest, ConversionConfigRequest
from ..services.conversion_service import conversion_service
from ..services.job_service import job_service
from ..services.progress_service import progress_service

router = APIRouter()


@router.post("/convert/start", tags=["Conversion"])
async def start_conversion(
    request: StartConversionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start converting uploaded files to MP3

    Args:
        request: Conversion request with job_id and configuration

    Returns:
        Success message with job_id
    """
    # Verify job exists
    job = job_service.get_job(db, request.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check if job is already processing or completed
    if job.status != "queued":
        raise HTTPException(
            status_code=400,
            detail=f"Job is already {job.status}"
        )

    # Update job configuration
    job.bitrate = request.config.bitrate
    job.sample_rate = request.config.sample_rate
    job.preserve_metadata = request.config.preserve_metadata
    db.commit()

    # Start conversion in background
    # Note: progress updates will be sent via SSE
    background_tasks.add_task(
        conversion_service.convert_job,
        request.job_id,
        db
    )

    return {
        "message": "Conversion started",
        "job_id": request.job_id,
        "status": "processing"
    }


@router.get("/convert/status/{job_id}", tags=["Conversion"])
async def get_conversion_status(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Get current status of a conversion job

    Args:
        job_id: Job ID

    Returns:
        Job status information
    """
    job = job_service.get_job_with_files(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.delete("/convert/cancel/{job_id}", tags=["Conversion"])
async def cancel_conversion(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Cancel an active conversion job

    Args:
        job_id: Job ID

    Returns:
        Success message
    """
    # Verify job exists
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check if job is active
    if not conversion_service.is_job_active(job_id):
        raise HTTPException(
            status_code=400,
            detail="Job is not currently processing"
        )

    # Cancel the job
    success = await conversion_service.cancel_job(job_id, db)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to cancel job")

    return {
        "message": "Conversion cancelled",
        "job_id": job_id,
        "status": "cancelled"
    }


@router.get("/progress/{job_id}", tags=["Conversion"])
async def stream_job_progress(
    job_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Stream real-time progress updates for a job via Server-Sent Events (SSE)

    Args:
        job_id: Job ID
        request: FastAPI request

    Returns:
        SSE stream with progress updates

    Events:
        - connected: Initial connection confirmation
        - file_progress: Progress update for a file
        - file_completed: File conversion completed
        - job_completed: All files completed
        - error: Error occurred
    """
    # Verify job exists
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Return SSE stream
    return await progress_service.stream_progress(job_id, request)
