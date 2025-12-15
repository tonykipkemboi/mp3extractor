"use client";

import { File, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { formatFileSize } from "@/lib/utils";
import { cn } from "@/lib/utils";

interface FileListProps {
  files: File[];
  onRemove?: (index: number) => void;
  disabled?: boolean;
}

export function FileList({ files, onRemove, disabled = false }: FileListProps) {
  if (files.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-base font-bold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent dark:from-slate-100 dark:to-slate-300">
          Selected Files ({files.length})
        </h3>
      </div>

      <div className="space-y-2">
        {files.map((file, index) => (
          <div
            key={`${file.name}-${index}`}
            className={cn(
              "group flex items-center gap-3 p-4 rounded-xl border-2 transition-all duration-300",
              "glass-card hover:shadow-lg hover:scale-[1.01] hover:border-blue-400/50",
              disabled && "opacity-60"
            )}
          >
            <div className="p-2.5 bg-gradient-to-br from-blue-100 to-violet-100 dark:from-blue-950 dark:to-violet-950 rounded-lg transition-all duration-300 group-hover:scale-110 group-hover:shadow-md">
              <File className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>

            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold truncate text-slate-800 dark:text-slate-200">{file.name}</p>
              <p className="text-xs text-muted-foreground font-medium">
                {formatFileSize(file.size)}
              </p>
            </div>

            {onRemove && !disabled && (
              <Button
                variant="ghost"
                size="icon"
                className="h-9 w-9 shrink-0 hover:bg-red-100 hover:text-red-600 dark:hover:bg-red-950 dark:hover:text-red-400 transition-all duration-200"
                onClick={() => onRemove(index)}
              >
                <X className="w-4 h-4" />
                <span className="sr-only">Remove file</span>
              </Button>
            )}
          </div>
        ))}
      </div>

      <div className="flex items-center justify-between pt-2 px-2">
        <span className="text-sm font-medium text-slate-600 dark:text-slate-400">Total size:</span>
        <span className="text-sm font-bold bg-gradient-to-r from-blue-600 to-violet-600 bg-clip-text text-transparent">
          {formatFileSize(files.reduce((acc, file) => acc + file.size, 0))}
        </span>
      </div>
    </div>
  );
}
