"use client";

import { Download, CheckCircle2, XCircle, Loader2, File } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { formatProgress } from "@/lib/utils";
import { apiClient } from "@/lib/api-client";

interface FileProgress {
  filename: string;
  progress: number;
  status: "pending" | "processing" | "completed" | "failed";
  error?: string;
}

interface ConversionProgressProps {
  jobId: string;
  filesProgress: FileProgress[];
  isCompleted: boolean;
}

export function ConversionProgress({
  jobId,
  filesProgress,
  isCompleted,
}: ConversionProgressProps) {
  const handleDownloadFile = (filename: string) => {
    const url = apiClient.getDownloadUrl(jobId, filename.replace(".mp4", ".mp3"));
    window.open(url, "_blank");
  };

  const handleDownloadAll = () => {
    const url = apiClient.getDownloadZipUrl(jobId);
    window.open(url, "_blank");
  };

  const completedCount = filesProgress.filter((f) => f.status === "completed").length;
  const canDownloadAll = isCompleted && completedCount > 0;

  return (
    <Card className="glass-card shadow-lg border-2">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl">Files</CardTitle>
          {canDownloadAll && (
            <Button
              onClick={handleDownloadAll}
              variant="outline"
              size="sm"
              className="border-2 hover:bg-gradient-to-r hover:from-blue-50 hover:to-violet-50 dark:hover:from-blue-950 dark:hover:to-violet-950 transition-all duration-300"
            >
              <Download className="w-4 h-4 mr-2" />
              Download All (ZIP)
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent>
        <div className="space-y-3">
          {filesProgress.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              No files to display
            </div>
          ) : (
            filesProgress.map((file) => (
              <div
                key={file.filename}
                className="flex items-center gap-3 p-4 rounded-xl border-2 glass-card transition-all duration-300 hover:shadow-md"
              >
                {/* Icon */}
                <div className="shrink-0">
                  {file.status === "completed" && (
                    <div className="p-2.5 bg-gradient-to-br from-green-100 to-emerald-100 dark:from-green-950 dark:to-emerald-950 rounded-lg">
                      <CheckCircle2 className="w-5 h-5 text-green-600 dark:text-green-400" />
                    </div>
                  )}
                  {file.status === "processing" && (
                    <div className="p-2.5 bg-gradient-to-br from-blue-100 to-violet-100 dark:from-blue-950 dark:to-violet-950 rounded-lg">
                      <Loader2 className="w-5 h-5 text-blue-600 dark:text-blue-400 animate-spin" />
                    </div>
                  )}
                  {file.status === "failed" && (
                    <div className="p-2.5 bg-gradient-to-br from-red-100 to-rose-100 dark:from-red-950 dark:to-rose-950 rounded-lg">
                      <XCircle className="w-5 h-5 text-red-600 dark:text-red-400" />
                    </div>
                  )}
                  {file.status === "pending" && (
                    <div className="p-2.5 bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-800 dark:to-slate-900 rounded-lg">
                      <File className="w-5 h-5 text-slate-600 dark:text-slate-400" />
                    </div>
                  )}
                </div>

                {/* File Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <p className="text-sm font-semibold truncate text-slate-800 dark:text-slate-200">
                      {file.filename}
                    </p>
                    <Badge
                      variant={
                        file.status === "completed"
                          ? "default"
                          : file.status === "failed"
                          ? "destructive"
                          : "secondary"
                      }
                      className="shrink-0 font-medium"
                    >
                      {file.status}
                    </Badge>
                  </div>

                  {/* Progress Bar (for processing files) */}
                  {file.status === "processing" && (
                    <div className="flex items-center gap-2">
                      <Progress value={file.progress * 100} className="h-2" />
                      <span className="text-xs text-muted-foreground shrink-0 font-semibold">
                        {formatProgress(file.progress)}
                      </span>
                    </div>
                  )}

                  {/* Error Message */}
                  {file.status === "failed" && file.error && (
                    <p className="text-xs text-red-600 dark:text-red-400 mt-1 font-medium">{file.error}</p>
                  )}

                  {/* Success Message */}
                  {file.status === "completed" && (
                    <p className="text-xs text-green-600 dark:text-green-400 mt-1 font-medium">
                      Converted successfully
                    </p>
                  )}
                </div>

                {/* Download Button */}
                {file.status === "completed" && (
                  <Button
                    onClick={() => handleDownloadFile(file.filename)}
                    variant="ghost"
                    size="icon"
                    className="shrink-0 hover:bg-blue-100 hover:text-blue-600 dark:hover:bg-blue-950 dark:hover:text-blue-400 transition-all duration-200"
                  >
                    <Download className="w-4 h-4" />
                    <span className="sr-only">Download</span>
                  </Button>
                )}
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
