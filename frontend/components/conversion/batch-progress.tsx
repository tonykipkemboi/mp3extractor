"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { formatProgress } from "@/lib/utils";

interface BatchProgressProps {
  totalFiles: number;
  completedFiles: number;
  failedFiles: number;
  overallProgress: number;
  isCompleted: boolean;
}

export function BatchProgress({
  totalFiles,
  completedFiles,
  failedFiles,
  overallProgress,
  isCompleted,
}: BatchProgressProps) {
  const processingFiles = totalFiles - completedFiles - failedFiles;
  const successRate = totalFiles > 0 ? (completedFiles / totalFiles) * 100 : 0;

  return (
    <Card className="glass-card shadow-lg border-2">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl">Conversion Progress</CardTitle>
          {isCompleted ? (
            <Badge variant={failedFiles > 0 ? "destructive" : "default"} className="font-semibold">
              {failedFiles > 0 ? "Completed with errors" : "Completed"}
            </Badge>
          ) : (
            <Badge variant="secondary" className="font-semibold">
              <Loader2 className="w-3 h-3 mr-1 animate-spin" />
              Processing
            </Badge>
          )}
        </div>
        <CardDescription className="text-sm">
          Converting {totalFiles} file{totalFiles !== 1 ? "s" : ""} to MP3
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Overall Progress Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-600 dark:text-slate-400 font-medium">Overall Progress</span>
            <span className="font-bold bg-gradient-to-r from-blue-600 to-violet-600 bg-clip-text text-transparent">{formatProgress(overallProgress)}</span>
          </div>
          <Progress value={overallProgress * 100} className="h-3" />
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-4">
          {/* Completed */}
          <div className="flex flex-col items-center p-4 rounded-xl bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/30 dark:to-emerald-950/30 border-2 border-green-500/30 shadow-md transition-all duration-300">
            <CheckCircle2 className="w-6 h-6 text-green-600 dark:text-green-400 mb-2" />
            <span className="text-2xl font-bold text-green-600 dark:text-green-400">
              {completedFiles}
            </span>
            <span className="text-xs text-muted-foreground font-medium">Completed</span>
          </div>

          {/* Processing - only show animation when actually processing */}
          <div className={`flex flex-col items-center p-4 rounded-xl transition-all duration-300 ${
            processingFiles > 0 && !isCompleted
              ? "bg-gradient-to-br from-blue-50 to-violet-50 dark:from-blue-950/30 dark:to-violet-950/30 border-2 border-blue-500/30 shadow-md"
              : "bg-muted/30 border-2 border-muted/40"
          }`}>
            <Loader2 className={`w-6 h-6 mb-2 ${
              processingFiles > 0 && !isCompleted
                ? "text-blue-600 dark:text-blue-400 animate-spin"
                : "text-muted-foreground/50"
            }`} />
            <span className={`text-2xl font-bold ${
              processingFiles > 0 && !isCompleted
                ? "text-blue-600 dark:text-blue-400"
                : "text-muted-foreground/50"
            }`}>
              {processingFiles}
            </span>
            <span className="text-xs text-muted-foreground font-medium">Processing</span>
          </div>

          {/* Failed - only show red when there are actual failures */}
          <div className={`flex flex-col items-center p-4 rounded-xl transition-all duration-300 ${
            failedFiles > 0
              ? "bg-gradient-to-br from-red-50 to-rose-50 dark:from-red-950/30 dark:to-rose-950/30 border-2 border-red-500/30 shadow-md"
              : "bg-muted/30 border-2 border-muted/40"
          }`}>
            <XCircle className={`w-6 h-6 mb-2 ${
              failedFiles > 0
                ? "text-red-600 dark:text-red-400"
                : "text-muted-foreground/50"
            }`} />
            <span className={`text-2xl font-bold ${
              failedFiles > 0
                ? "text-red-600 dark:text-red-400"
                : "text-muted-foreground/50"
            }`}>
              {failedFiles}
            </span>
            <span className="text-xs text-muted-foreground font-medium">Failed</span>
          </div>
        </div>

        {/* Success Rate (when completed) */}
        {isCompleted && (
          <div className="pt-4 border-t-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-600 dark:text-slate-400 font-medium">Success Rate</span>
              <span className="font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">{successRate.toFixed(1)}%</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
