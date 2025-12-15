/**
 * API Request and Response Types
 */

// Conversion Configuration
export interface ConversionConfig {
  bitrate: string;
  sample_rate: number | null;
  preserve_metadata: boolean;
}

// Upload Response
export interface UploadResponse {
  job_id: string;
  files_uploaded: number;
  filenames: string[];
}

// Start Conversion Request
export interface StartConversionRequest {
  job_id: string;
  config: ConversionConfig;
}

// Start Conversion Response
export interface StartConversionResponse {
  message: string;
  job_id: string;
  status: string;
}

// Health Check Response
export interface HealthResponse {
  status: string;
  version: string;
  database: string;
}

// Error Response
export interface ErrorResponse {
  detail: string;
}
