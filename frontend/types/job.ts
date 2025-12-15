/**
 * Job and File Types
 */

export type JobStatus = "queued" | "processing" | "completed" | "failed" | "cancelled";
export type FileStatus = "pending" | "processing" | "completed" | "failed";

// Job File
export interface JobFile {
  id: number;
  job_id: string;
  input_filename: string;
  output_filename: string | null;
  status: FileStatus;
  file_size: number | null;
  output_size: number | null;
  progress: number;
  duration_seconds: number | null;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

// Job
export interface Job {
  job_id: string;
  status: JobStatus;
  created_at: string;
  updated_at: string;
  started_at: string | null;
  completed_at: string | null;
  bitrate: string;
  sample_rate: number | null;
  preserve_metadata: boolean;
  total_files: number;
  completed_files: number;
  failed_files: number;
  overall_progress: number;
  error_message: string | null;
  output_path: string | null;
  files: JobFile[];
}

// Job List Response
export interface JobListResponse {
  jobs: Job[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// SSE Event Types
export type SSEEventType =
  | "connected"
  | "file_progress"
  | "file_completed"
  | "job_completed"
  | "error";

// SSE Event Data
export interface SSEEventData {
  job_id: string;
  [key: string]: any;
}

// File Progress Event
export interface FileProgressEvent extends SSEEventData {
  filename: string;
  progress: number;
  current_ms: number;
  total_ms: number;
}

// File Completed Event
export interface FileCompletedEvent extends SSEEventData {
  filename: string;
  output_filename: string;
  output_size: number;
}

// Job Completed Event
export interface JobCompletedEvent extends SSEEventData {
  total_files: number;
  completed_files: number;
  failed_files: number;
}

// Error Event
export interface ErrorEvent extends SSEEventData {
  filename?: string;
  error: string;
}
