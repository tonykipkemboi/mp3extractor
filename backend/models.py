"""
SQLAlchemy ORM models
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Job(Base):
    """
    Job model - represents a conversion job
    """
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    status = Column(String, nullable=False, index=True)  # queued, processing, completed, failed, cancelled

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Configuration
    bitrate = Column(String, nullable=False, default='320k')
    sample_rate = Column(Integer, nullable=True)
    preserve_metadata = Column(Boolean, default=True, nullable=False)

    # Progress tracking
    total_files = Column(Integer, nullable=False)
    completed_files = Column(Integer, default=0, nullable=False)
    failed_files = Column(Integer, default=0, nullable=False)
    overall_progress = Column(Float, default=0.0, nullable=False)  # 0.0 to 1.0

    # Error information
    error_message = Column(Text, nullable=True)

    # Storage
    output_path = Column(String, nullable=True)

    # Relationships
    files = relationship("JobFile", back_populates="job", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Job(id={self.id}, status={self.status}, files={self.total_files})>"


class JobFile(Base):
    """
    JobFile model - represents a single file in a job
    """
    __tablename__ = "job_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)

    # File information
    input_filename = Column(String, nullable=False)
    output_filename = Column(String, nullable=True)

    # Status
    status = Column(String, nullable=False, index=True)  # queued, processing, completed, failed

    # Size tracking
    file_size = Column(Integer, nullable=True)  # Input file size in bytes
    output_size = Column(Integer, nullable=True)  # Output file size in bytes

    # Progress
    progress = Column(Float, default=0.0, nullable=False)  # 0.0 to 1.0
    duration_seconds = Column(Float, nullable=True)  # Audio duration

    # Timestamps
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Error information
    error_message = Column(Text, nullable=True)

    # Relationships
    job = relationship("Job", back_populates="files")

    def __repr__(self):
        return f"<JobFile(id={self.id}, filename={self.input_filename}, status={self.status})>"
