"use client";

import { useState, useEffect, useCallback } from "react";
import { apiClient } from "@/lib/api-client";
import { Job, JobListResponse } from "@/types/job";
import { toast } from "sonner";

interface UseJobsResult {
  jobs: Job[];
  loading: boolean;
  error: string | null;
  page: number;
  totalPages: number;
  total: number;
  fetchJobs: (page?: number, status?: string) => Promise<void>;
  deleteJob: (jobId: string) => Promise<void>;
  clearHistory: (daysOld?: number) => Promise<void>;
  refresh: () => Promise<void>;
}

export function useJobs(initialPage: number = 1, pageSize: number = 20): UseJobsResult {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(initialPage);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState<string | undefined>();

  const fetchJobs = useCallback(async (newPage?: number, status?: string) => {
    try {
      setLoading(true);
      setError(null);

      const targetPage = newPage ?? page;
      const targetStatus = status ?? statusFilter;

      const response: JobListResponse = await apiClient.listJobs(
        targetPage,
        pageSize,
        targetStatus
      );

      setJobs(response.jobs);
      setPage(response.page);
      setTotalPages(response.total_pages);
      setTotal(response.total);
      setStatusFilter(targetStatus);
    } catch (err) {
      const errorMessage = apiClient.handleError(err);
      setError(errorMessage);
      toast.error(`Failed to load jobs: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, statusFilter]);

  const deleteJob = useCallback(async (jobId: string) => {
    try {
      await apiClient.deleteJob(jobId);
      toast.success("Job deleted successfully");
      // Refresh the list
      await fetchJobs();
    } catch (err) {
      const errorMessage = apiClient.handleError(err);
      toast.error(`Failed to delete job: ${errorMessage}`);
      throw err;
    }
  }, [fetchJobs]);

  const clearHistory = useCallback(async (daysOld: number = 7) => {
    try {
      const result = await apiClient.clearHistory(daysOld);
      toast.success(`Deleted ${result.deleted} old job(s)`);
      // Refresh the list
      await fetchJobs();
    } catch (err) {
      const errorMessage = apiClient.handleError(err);
      toast.error(`Failed to clear history: ${errorMessage}`);
      throw err;
    }
  }, [fetchJobs]);

  const refresh = useCallback(async () => {
    await fetchJobs(page, statusFilter);
  }, [fetchJobs, page, statusFilter]);

  // Initial fetch
  useEffect(() => {
    fetchJobs();
  }, []); // Only on mount

  return {
    jobs,
    loading,
    error,
    page,
    totalPages,
    total,
    fetchJobs,
    deleteJob,
    clearHistory,
    refresh,
  };
}
