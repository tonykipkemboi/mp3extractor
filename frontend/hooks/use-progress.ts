"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { SSEClient } from "@/lib/sse-client";
import type {
  SSEEventType,
  SSEEventData,
  FileProgressEvent,
  FileCompletedEvent,
  JobCompletedEvent,
  ErrorEvent,
} from "@/types/job";

interface FileProgress {
  filename: string;
  progress: number;
  status: "pending" | "processing" | "completed" | "failed";
  error?: string;
}

interface ProgressState {
  connected: boolean;
  filesProgress: Map<string, FileProgress>;
  completedFiles: string[];
  failedFiles: string[];
  isCompleted: boolean;
  error?: string;
}

export function useProgress(jobId: string | null) {
  const [state, setState] = useState<ProgressState>({
    connected: false,
    filesProgress: new Map(),
    completedFiles: [],
    failedFiles: [],
    isCompleted: false,
  });

  const sseClientRef = useRef<SSEClient | null>(null);

  const handleEvent = useCallback((eventType: SSEEventType, data: SSEEventData) => {
    setState((prev) => {
      const newState = { ...prev };

      switch (eventType) {
        case "connected":
          newState.connected = true;
          break;

        case "file_progress": {
          const progressData = data as FileProgressEvent;
          const newProgress = new Map(prev.filesProgress);
          newProgress.set(progressData.filename, {
            filename: progressData.filename,
            progress: progressData.progress,
            status: "processing",
          });
          newState.filesProgress = newProgress;
          break;
        }

        case "file_completed": {
          const completedData = data as FileCompletedEvent;
          const newProgress = new Map(prev.filesProgress);
          newProgress.set(completedData.filename, {
            filename: completedData.filename,
            progress: 1.0,
            status: "completed",
          });
          newState.filesProgress = newProgress;
          newState.completedFiles = [...prev.completedFiles, completedData.filename];
          break;
        }

        case "job_completed": {
          const jobData = data as JobCompletedEvent;
          newState.isCompleted = true;
          newState.connected = false;
          break;
        }

        case "error": {
          const errorData = data as ErrorEvent;
          if (errorData.filename) {
            const newProgress = new Map(prev.filesProgress);
            newProgress.set(errorData.filename, {
              filename: errorData.filename,
              progress: 0,
              status: "failed",
              error: errorData.error,
            });
            newState.filesProgress = newProgress;
            newState.failedFiles = [...prev.failedFiles, errorData.filename];
          } else {
            newState.error = errorData.error;
          }
          break;
        }
      }

      return newState;
    });
  }, []);

  useEffect(() => {
    if (!jobId) {
      return;
    }

    // Create SSE client
    const client = new SSEClient(jobId);
    sseClientRef.current = client;

    // Subscribe to events
    const unsubscribe = client.onEvent(handleEvent);

    // Connect
    client.connect();

    // Cleanup
    return () => {
      unsubscribe();
      client.disconnect();
      sseClientRef.current = null;
    };
  }, [jobId, handleEvent]);

  // Calculate overall progress
  const overallProgress = Array.from(state.filesProgress.values()).reduce(
    (sum, file) => sum + file.progress,
    0
  ) / Math.max(state.filesProgress.size, 1);

  return {
    connected: state.connected,
    filesProgress: Array.from(state.filesProgress.values()),
    completedFiles: state.completedFiles,
    failedFiles: state.failedFiles,
    isCompleted: state.isCompleted,
    overallProgress,
    error: state.error,
  };
}
