"use client";

import { useState } from "react";
import { Download, Trash2, RefreshCw } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { JobStatusBadge } from "./job-status-badge";
import { formatRelativeTime, formatFileSize } from "@/lib/utils";
import { apiClient } from "@/lib/api-client";
import type { Job } from "@/types/job";

interface JobHistoryTableProps {
  jobs: Job[];
  loading: boolean;
  onDelete: (jobId: string) => Promise<void>;
  onRefresh: () => void;
}

export function JobHistoryTable({
  jobs,
  loading,
  onDelete,
  onRefresh,
}: JobHistoryTableProps) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [jobToDelete, setJobToDelete] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);

  const handleDownloadZip = (jobId: string) => {
    const url = apiClient.getDownloadZipUrl(jobId);
    window.open(url, "_blank");
  };

  const handleDeleteClick = (jobId: string) => {
    setJobToDelete(jobId);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!jobToDelete) return;

    setDeleting(true);
    try {
      await onDelete(jobToDelete);
      setDeleteDialogOpen(false);
      setJobToDelete(null);
    } catch (error) {
      // Error is handled in the parent
    } finally {
      setDeleting(false);
    }
  };

  if (loading && jobs.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent" />
        <p className="mt-4 text-lg text-muted-foreground">Loading jobs...</p>
      </div>
    );
  }

  if (jobs.length === 0) {
    return (
      <div className="text-center py-12 border rounded-lg">
        <p className="text-lg text-muted-foreground">No jobs found</p>
        <p className="text-sm text-muted-foreground mt-2">
          Start a conversion to see it here
        </p>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-4">
        {/* Refresh Button */}
        <div className="flex justify-end">
          <Button
            onClick={onRefresh}
            variant="outline"
            size="sm"
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>

        {/* Table */}
        <div className="border rounded-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Status</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Filenames</TableHead>
                <TableHead>Files</TableHead>
                <TableHead>Quality</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {jobs.map((job) => {
                const canDownload =
                  job.status === "completed" && job.completed_files > 0;

                return (
                  <TableRow key={job.job_id}>
                    {/* Status */}
                    <TableCell>
                      <JobStatusBadge status={job.status} />
                    </TableCell>

                    {/* Date */}
                    <TableCell>
                      <div className="text-sm">
                        {formatRelativeTime(job.created_at)}
                      </div>
                    </TableCell>

                    {/* Filenames */}
                    <TableCell>
                      <div className="max-w-xs">
                        {job.files && job.files.length > 0 ? (
                          <div className="space-y-1">
                            {job.files.slice(0, 2).map((file) => (
                              <div key={`${job.job_id}-${file.input_filename}`} className="text-sm truncate" title={file.input_filename}>
                                {file.input_filename}
                              </div>
                            ))}
                            {job.files.length > 2 && (
                              <div className="text-xs text-muted-foreground">
                                +{job.files.length - 2} more
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="text-sm text-muted-foreground">
                            {job.total_files} file{job.total_files !== 1 ? "s" : ""}
                          </div>
                        )}
                      </div>
                    </TableCell>

                    {/* Files Count */}
                    <TableCell>
                      <div className="text-sm">
                        <div className="font-medium">{job.completed_files} / {job.total_files}</div>
                        {job.failed_files > 0 && (
                          <div className="text-xs text-red-600">
                            {job.failed_files} failed
                          </div>
                        )}
                      </div>
                    </TableCell>

                    {/* Quality */}
                    <TableCell>
                      <div className="text-sm font-medium">{job.bitrate || "320k"}</div>
                      {job.sample_rate && (
                        <div className="text-xs text-muted-foreground">
                          {(job.sample_rate / 1000).toFixed(1)} kHz
                        </div>
                      )}
                      {job.preserve_metadata && (
                        <div className="text-xs text-muted-foreground">
                          +metadata
                        </div>
                      )}
                    </TableCell>

                    {/* Actions */}
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        {canDownload && (
                          <Button
                            key={`download-${job.job_id}`}
                            onClick={() => handleDownloadZip(job.job_id)}
                            variant="outline"
                            size="sm"
                          >
                            <Download className="w-4 h-4 mr-2" />
                            Download
                          </Button>
                        )}
                        <Button
                          key={`delete-${job.job_id}`}
                          onClick={() => handleDeleteClick(job.job_id)}
                          variant="ghost"
                          size="sm"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Job</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this job? This will remove all
              associated files and cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
              disabled={deleting}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleConfirmDelete}
              disabled={deleting}
            >
              {deleting ? "Deleting..." : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
