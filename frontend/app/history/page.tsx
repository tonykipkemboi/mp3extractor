"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { JobHistoryTable } from "@/components/history/job-history-table";
import { useJobs } from "@/hooks/use-jobs";
import { ChevronLeft, ChevronRight, Trash2 } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

export default function HistoryPage() {
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [clearDialogOpen, setClearDialogOpen] = useState(false);
  const [clearing, setClearing] = useState(false);

  const { jobs, loading, page, totalPages, total, fetchJobs, deleteJob, clearHistory, refresh } =
    useJobs();

  const handleFilterChange = (value: string) => {
    const filter = value === "all" ? undefined : value;
    setStatusFilter(filter);
    fetchJobs(1, filter);
  };

  const handlePageChange = (newPage: number) => {
    fetchJobs(newPage, statusFilter);
  };

  const handleClearHistory = async () => {
    setClearing(true);
    try {
      await clearHistory(7); // Clear jobs older than 7 days
      setClearDialogOpen(false);
    } catch (error) {
      // Error is handled in the hook
    } finally {
      setClearing(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold">Job History</h1>
          <p className="text-lg text-muted-foreground mt-2">
            View and manage your conversion jobs
          </p>
        </div>
        <Button
          onClick={() => setClearDialogOpen(true)}
          variant="outline"
          disabled={total === 0}
        >
          <Trash2 className="w-4 h-4 mr-2" />
          Clear Old Jobs
        </Button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium">Status:</label>
          <Select
            value={statusFilter || "all"}
            onValueChange={handleFilterChange}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="All statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="queued">Queued</SelectItem>
              <SelectItem value="processing">Processing</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="failed">Failed</SelectItem>
              <SelectItem value="cancelled">Cancelled</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex-1" />

        <div className="text-sm text-muted-foreground">
          Showing {jobs.length} of {total} job{total !== 1 ? "s" : ""}
        </div>
      </div>

      {/* Table */}
      <JobHistoryTable
        jobs={jobs}
        loading={loading}
        onDelete={deleteJob}
        onRefresh={refresh}
      />

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <Button
            onClick={() => handlePageChange(page - 1)}
            disabled={page === 1 || loading}
            variant="outline"
          >
            <ChevronLeft className="w-4 h-4 mr-2" />
            Previous
          </Button>

          <div className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </div>

          <Button
            onClick={() => handlePageChange(page + 1)}
            disabled={page === totalPages || loading}
            variant="outline"
          >
            Next
            <ChevronRight className="w-4 h-4 ml-2" />
          </Button>
        </div>
      )}

      {/* Clear History Dialog */}
      <Dialog open={clearDialogOpen} onOpenChange={setClearDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Clear Old Jobs</DialogTitle>
            <DialogDescription>
              This will permanently delete all jobs and their files that are older
              than 7 days. This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setClearDialogOpen(false)}
              disabled={clearing}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleClearHistory}
              disabled={clearing}
            >
              {clearing ? "Clearing..." : "Clear History"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
