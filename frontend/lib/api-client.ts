/**
 * API Client - Type-safe API calls to FastAPI backend
 */

import axios, { AxiosInstance, AxiosError } from "axios";
import type {
  ConversionConfig,
  UploadResponse,
  StartConversionRequest,
  StartConversionResponse,
  HealthResponse,
  ErrorResponse,
} from "@/types/api";
import type { Job, JobListResponse } from "@/types/job";

class APIClient {
  private client: AxiosInstance;

  constructor() {
    const baseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    this.client = axios.create({
      baseURL,
      headers: {
        "Content-Type": "application/json",
      },
      timeout: 30000, // 30 seconds
    });
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>("/api/health");
    return response.data;
  }

  /**
   * Upload files
   */
  async uploadFiles(files: File[]): Promise<UploadResponse> {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });

    const response = await this.client.post<UploadResponse>(
      "/api/v1/files/upload",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        timeout: 120000, // 2 minutes for large uploads
      }
    );

    return response.data;
  }

  /**
   * Start conversion
   */
  async startConversion(
    jobId: string,
    config: ConversionConfig
  ): Promise<StartConversionResponse> {
    const request: StartConversionRequest = {
      job_id: jobId,
      config,
    };

    const response = await this.client.post<StartConversionResponse>(
      "/api/v1/convert/start",
      request
    );

    return response.data;
  }

  /**
   * Get conversion status
   */
  async getConversionStatus(jobId: string): Promise<Job> {
    const response = await this.client.get<Job>(
      `/api/v1/convert/status/${jobId}`
    );
    return response.data;
  }

  /**
   * Cancel conversion
   */
  async cancelConversion(jobId: string): Promise<void> {
    await this.client.delete(`/api/v1/convert/cancel/${jobId}`);
  }

  /**
   * Get download URL for a single file
   */
  getDownloadUrl(jobId: string, filename: string): string {
    const baseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    return `${baseURL}/api/v1/files/download/${jobId}/${filename}`;
  }

  /**
   * Get download URL for ZIP file
   */
  getDownloadZipUrl(jobId: string): string {
    const baseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    return `${baseURL}/api/v1/files/download-zip/${jobId}`;
  }

  /**
   * Download single file
   */
  async downloadFile(jobId: string, filename: string): Promise<Blob> {
    const response = await this.client.get(
      `/api/v1/files/download/${jobId}/${filename}`,
      {
        responseType: "blob",
      }
    );
    return response.data;
  }

  /**
   * Download ZIP file
   */
  async downloadZip(jobId: string): Promise<Blob> {
    const response = await this.client.get(
      `/api/v1/files/download-zip/${jobId}`,
      {
        responseType: "blob",
      }
    );
    return response.data;
  }

  /**
   * List jobs
   */
  async listJobs(
    page: number = 1,
    pageSize: number = 20,
    status?: string
  ): Promise<JobListResponse> {
    const params: any = { page, page_size: pageSize };
    if (status) {
      params.status = status;
    }

    const response = await this.client.get<JobListResponse>("/api/v1/jobs", {
      params,
    });
    return response.data;
  }

  /**
   * Get job details
   */
  async getJob(jobId: string): Promise<Job> {
    const response = await this.client.get<Job>(`/api/v1/jobs/${jobId}`);
    return response.data;
  }

  /**
   * Delete job
   */
  async deleteJob(jobId: string): Promise<void> {
    await this.client.delete(`/api/v1/jobs/${jobId}`);
  }

  /**
   * Clear old jobs
   */
  async clearHistory(daysOld: number = 7): Promise<{ deleted: number }> {
    const response = await this.client.post<{ deleted: number }>(
      "/api/v1/jobs/clear-history",
      { days_old: daysOld }
    );
    return response.data;
  }

  /**
   * Handle API errors
   */
  handleError(error: unknown): string {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ErrorResponse>;
      if (axiosError.response?.data?.detail) {
        return axiosError.response.data.detail;
      }
      return axiosError.message;
    }
    return "An unexpected error occurred";
  }
}

// Export singleton instance
export const apiClient = new APIClient();
