"use client";

import { useCallback, useState } from "react";
import { Upload, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface FileUploadZoneProps {
  onFilesSelected: (files: File[]) => void;
  disabled?: boolean;
}

export function FileUploadZone({ onFilesSelected, disabled = false }: FileUploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) {
      setIsDragging(true);
    }
  }, [disabled]);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (disabled) return;

    const files = Array.from(e.dataTransfer.files).filter(
      (file) => file.type === "video/mp4" || file.name.endsWith(".mp4")
    );

    if (files.length > 0) {
      onFilesSelected(files);
    }
  }, [disabled, onFilesSelected]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      onFilesSelected(files);
    }
    // Reset input
    e.target.value = "";
  }, [onFilesSelected]);

  return (
    <div
      className={cn(
        "relative border-2 border-dashed rounded-2xl p-16 text-center transition-all duration-300 group",
        isDragging && !disabled
          ? "border-blue-500 bg-gradient-to-br from-blue-50 to-violet-50 scale-[1.02] shadow-xl shadow-blue-500/20 dark:from-blue-950/30 dark:to-violet-950/30"
          : "border-slate-300 hover:border-blue-400 hover:bg-gradient-to-br hover:from-slate-50 hover:to-blue-50/50 hover:shadow-lg dark:border-slate-700 dark:hover:border-blue-500 dark:hover:from-slate-900/50 dark:hover:to-blue-950/30",
        disabled && "opacity-50 cursor-not-allowed"
      )}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
    >
      {/* Animated background gradient */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-400/0 via-violet-400/5 to-blue-400/0 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />

      <input
        type="file"
        id="file-upload"
        className="hidden"
        accept=".mp4,video/mp4"
        multiple
        onChange={handleFileSelect}
        disabled={disabled}
      />

      <label
        htmlFor="file-upload"
        className={cn(
          "cursor-pointer relative z-10",
          disabled && "cursor-not-allowed"
        )}
      >
        <div className="flex flex-col items-center gap-6">
          <div className={cn(
            "p-6 rounded-2xl transition-all duration-300",
            isDragging
              ? "bg-gradient-to-br from-blue-500 to-violet-600 scale-110 shadow-2xl"
              : "bg-gradient-to-br from-blue-100 to-violet-100 group-hover:scale-110 group-hover:shadow-xl dark:from-blue-950 dark:to-violet-950"
          )}>
            <Upload className={cn(
              "w-12 h-12 transition-colors",
              isDragging ? "text-white" : "text-blue-600 dark:text-blue-400"
            )} />
          </div>

          <div className="space-y-2">
            <p className="text-xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent dark:from-slate-100 dark:to-slate-300">
              Drop MP4 files here or click to browse
            </p>
            <p className="text-base text-slate-600 dark:text-slate-400">
              Upload one or multiple MP4 files to convert to MP3
            </p>
          </div>

          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-slate-100 dark:bg-slate-800 text-sm font-medium text-slate-700 dark:text-slate-300">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            Supported format: MP4
          </div>
        </div>
      </label>
    </div>
  );
}
