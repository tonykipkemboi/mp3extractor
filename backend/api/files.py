"""
File management API endpoints
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse, StreamingResponse
from typing import List
import uuid
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Job, JobFile
from ..schemas import UploadResponse
from ..services.file_service import file_service

router = APIRouter()


@router.post("/files/upload", response_model=UploadResponse, tags=["Files"])
async def upload_files(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload MP4 files for conversion

    Creates a new job and saves all uploaded files to storage.

    Args:
        files: List of MP4 files to upload

    Returns:
        UploadResponse with job_id and uploaded filenames
    """
    # Validate files
    for file in files:
        is_valid, error_msg = file_service.validate_upload_file(file.filename)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"{file.filename}: {error_msg}")

    # Check file count limit
    max_files = 50  # Can be moved to config
    if len(files) > max_files:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. Maximum {max_files} files allowed per job"
        )

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Save files
    try:
        uploaded_files = await file_service.save_multiple_uploads(files, job_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save files: {str(e)}")

    # Create job in database
    job = Job(
        id=job_id,
        status="queued",
        total_files=len(files),
        completed_files=0,
        failed_files=0,
        overall_progress=0.0
    )
    db.add(job)

    # Create job_files records
    for filename, file_path, file_size in uploaded_files:
        job_file = JobFile(
            job_id=job_id,
            input_filename=filename,
            status="queued",
            file_size=file_size,
            progress=0.0
        )
        db.add(job_file)

    db.commit()

    return UploadResponse(
        job_id=job_id,
        files_uploaded=len(files),
        filenames=[f[0] for f in uploaded_files]
    )


@router.get("/files/download/{job_id}/{filename}", tags=["Files"])
async def download_file(
    job_id: str,
    filename: str,
    db: Session = Depends(get_db)
):
    """
    Download a single converted MP3 file

    Args:
        job_id: Job ID
        filename: Output filename

    Returns:
        File download response
    """
    # Verify job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get file path
    file_path = file_service.get_output_file_path(job_id, filename)
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")

    # Return file
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@router.get("/files/download-zip/{job_id}", tags=["Files"])
async def download_all_files(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Download all converted files as a ZIP archive

    Args:
        job_id: Job ID

    Returns:
        ZIP file download response
    """
    # Verify job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Create ZIP archive
    zip_path = file_service.create_zip_archive(job_id)
    if not zip_path:
        raise HTTPException(status_code=404, detail="No files available for download")

    # Return ZIP file
    return FileResponse(
        path=zip_path,
        filename=f"converted_{job_id[:8]}.zip",
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="converted_{job_id[:8]}.zip"'
        }
    )


@router.delete("/files/cleanup/{job_id}", tags=["Files"])
async def cleanup_job_files(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Manually cleanup files for a job

    Deletes all uploaded and converted files for the job.

    Args:
        job_id: Job ID

    Returns:
        Success message
    """
    # Verify job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Cleanup files
    success = file_service.cleanup_job_files(job_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to cleanup files")

    return {"message": "Files cleaned up successfully", "job_id": job_id}


@router.get("/files/disk-usage/{job_id}", tags=["Files"])
async def get_job_disk_usage(
    job_id: str,
    db: Session = Depends(get_db)
):
    """
    Get disk usage for a job

    Args:
        job_id: Job ID

    Returns:
        Disk usage information
    """
    # Verify job exists
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get disk usage
    usage = file_service.get_job_disk_usage(job_id)

    return {
        "job_id": job_id,
        **usage
    }
