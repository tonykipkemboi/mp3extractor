"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { FileUploadZone } from "@/components/conversion/file-upload-zone";
import { FileList } from "@/components/conversion/file-list";
import { ConfigPanel } from "@/components/config/config-panel";
import { BatchProgress } from "@/components/conversion/batch-progress";
import { ConversionProgress } from "@/components/conversion/conversion-progress";
import { useConversion } from "@/hooks/use-conversion";
import { useProgress } from "@/hooks/use-progress";
import { ConversionConfig } from "@/types/api";
import { Play, RotateCcw } from "lucide-react";

export default function Home() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [config, setConfig] = useState<ConversionConfig>({
    bitrate: "320k",
    sample_rate: null,
    preserve_metadata: true,
  });

  const { state, jobId, uploadFiles, reset } = useConversion();
  const progress = useProgress(jobId);

  const handleFilesSelected = (files: File[]) => {
    setSelectedFiles((prev) => [...prev, ...files]);
  };

  const handleRemoveFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleStartConversion = async () => {
    if (selectedFiles.length === 0) return;
    await uploadFiles(selectedFiles, config);
  };

  const handleReset = () => {
    setSelectedFiles([]);
    reset();
  };

  const isUploading = state === "uploading";
  const isConverting = state === "converting";
  const isProcessing = isUploading || isConverting;
  const canStart = selectedFiles.length > 0 && !isProcessing;

  return (
    <div className="max-w-7xl mx-auto space-y-10 py-8">
      {/* Header */}
      <div className="text-center space-y-4 mb-12">
        <h1 className="text-5xl md:text-6xl font-bold tracking-tight">
          <span className="gradient-text">MP4</span> to <span className="gradient-text">MP3</span> Converter
        </h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Transform your video files into high-quality audio with lightning-fast conversion
        </p>
      </div>

      {/* Upload & Configuration Section (shown when not converting) */}
      {!isProcessing && !progress.isCompleted && (
        <div className="grid gap-8 lg:grid-cols-2">
          {/* Left Column: Upload */}
          <div className="space-y-4">
            <FileUploadZone
              onFilesSelected={handleFilesSelected}
              disabled={isProcessing}
            />
            <FileList
              files={selectedFiles}
              onRemove={handleRemoveFile}
              disabled={isProcessing}
            />
          </div>

          {/* Right Column: Configuration */}
          <div>
            <ConfigPanel
              config={config}
              onChange={setConfig}
              disabled={isProcessing}
            />
          </div>
        </div>
      )}

      {/* Action Buttons */}
      {!isProcessing && !progress.isCompleted && (
        <div className="flex items-center justify-center gap-4">
          <Button
            onClick={handleStartConversion}
            disabled={!canStart}
            size="lg"
            className="min-w-[220px] h-14 text-lg font-semibold gradient-primary hover:shadow-2xl hover:shadow-blue-500/50 hover:scale-105 transition-all duration-300"
          >
            <Play className="w-6 h-6 mr-2" />
            Start Conversion
          </Button>
          {selectedFiles.length > 0 && (
            <Button
              onClick={() => setSelectedFiles([])}
              variant="outline"
              size="lg"
              className="h-14 text-lg border-2 hover:bg-slate-100 dark:hover:bg-slate-800 transition-all duration-300"
            >
              Clear Files
            </Button>
          )}
        </div>
      )}

      {/* Progress Section (shown during and after conversion) */}
      {(isConverting || progress.isCompleted) && jobId && (
        <div className="space-y-6">
          {/* Batch Progress */}
          <BatchProgress
            totalFiles={selectedFiles.length}
            completedFiles={progress.completedFiles.length}
            failedFiles={progress.failedFiles.length}
            overallProgress={progress.overallProgress}
            isCompleted={progress.isCompleted}
          />

          {/* File-by-File Progress */}
          <ConversionProgress
            jobId={jobId}
            filesProgress={progress.filesProgress}
            isCompleted={progress.isCompleted}
          />

          {/* Reset Button (shown when completed) */}
          {progress.isCompleted && (
            <div className="flex items-center justify-center">
              <Button
                onClick={handleReset}
                size="lg"
                className="h-14 min-w-[240px] text-lg font-semibold gradient-primary hover:shadow-2xl hover:shadow-blue-500/50 hover:scale-105 transition-all duration-300"
              >
                <RotateCcw className="w-6 h-6 mr-2" />
                Convert More Files
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Loading State */}
      {isUploading && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent" />
          <p className="mt-4 text-lg font-medium">Uploading files...</p>
        </div>
      )}
    </div>
  );
}
