"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field, field_serializer
from typing import Optional, List
from datetime import datetime, timezone


# Configuration Schemas
class ConversionConfigRequest(BaseModel):
    """Configuration for conversion job"""
    bitrate: str = Field(default="320k", pattern="^[0-9]+k$")
    sample_rate: Optional[int] = Field(default=None, ge=8000, le=96000)
    preserve_metadata: bool = True


# File Schemas
class FileStatusResponse(BaseModel):
    """Status of a single file in a job"""
    input_filename: str
    status: str
    progress: float = Field(ge=0.0, le=1.0)
    output_filename: Optional[str] = None
    output_size: Optional[int] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


# Job Schemas
class JobCreateRequest(BaseModel):
    """Request to create a new job"""
    config: ConversionConfigRequest


class JobStatusResponse(BaseModel):
    """Full status of a conversion job"""
    job_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Configuration
    bitrate: str
    sample_rate: Optional[int]
    preserve_metadata: bool

    # Progress
    total_files: int
    completed_files: int
    failed_files: int
    overall_progress: float = Field(ge=0.0, le=1.0)

    # Files
    files: List[FileStatusResponse]

    # Error
    error_message: Optional[str] = None

    @field_serializer('created_at', 'updated_at', 'started_at', 'completed_at')
    def serialize_dt(self, dt: Optional[datetime]) -> Optional[str]:
        if dt is None:
            return None
        # Ensure datetime is in UTC and format with 'Z' suffix
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat().replace('+00:00', 'Z')

    class Config:
        from_attributes = True


class JobListItem(BaseModel):
    """Abbreviated job info for list view"""
    job_id: str
    status: str
    created_at: datetime
    total_files: int
    completed_files: int
    failed_files: int
    overall_progress: float

    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Paginated list of jobs"""
    jobs: List['JobStatusResponse']
    total: int
    page: int
    page_size: int


# Upload Response
class UploadResponse(BaseModel):
    """Response after successful file upload"""
    job_id: str
    files_uploaded: int
    filenames: List[str]


# Health Check
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    database: str


# Start Conversion Request
class StartConversionRequest(BaseModel):
    """Request to start a conversion job"""
    job_id: str
    config: ConversionConfigRequest
