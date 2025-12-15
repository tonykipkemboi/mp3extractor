"use client";

import { useState, useCallback } from "react";
import { apiClient } from "@/lib/api-client";
import { ConversionConfig } from "@/types/api";
import { toast } from "sonner";

type ConversionState = "idle" | "uploading" | "converting" | "completed" | "error";

interface UseConversionResult {
  state: ConversionState;
  jobId: string | null;
  error: string | null;
  uploadFiles: (files: File[], config: ConversionConfig) => Promise<void>;
  reset: () => void;
}

export function useConversion(): UseConversionResult {
  const [state, setState] = useState<ConversionState>("idle");
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const uploadFiles = useCallback(async (files: File[], config: ConversionConfig) => {
    try {
      setError(null);
      setState("uploading");

      // Upload files
      const uploadResponse = await apiClient.uploadFiles(files);
      toast.success(`Uploaded ${uploadResponse.files_uploaded} file(s)`, { duration: 2000 });

      setJobId(uploadResponse.job_id);

      // Start conversion
      setState("converting");
      await apiClient.startConversion(uploadResponse.job_id, config);
      toast.success("Conversion started - watch the progress below", { duration: 3000 });

    } catch (err) {
      const errorMessage = apiClient.handleError(err);
      setError(errorMessage);
      setState("error");
      toast.error(`Error: ${errorMessage}`);
    }
  }, []);

  const reset = useCallback(() => {
    setState("idle");
    setJobId(null);
    setError(null);
  }, []);

  return {
    state,
    jobId,
    error,
    uploadFiles,
    reset,
  };
}
