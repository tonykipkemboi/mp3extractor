import { Badge } from "@/components/ui/badge";
import { CheckCircle2, XCircle, Loader2, Clock, Ban } from "lucide-react";
import type { JobStatus } from "@/types/job";

interface JobStatusBadgeProps {
  status: JobStatus;
}

export function JobStatusBadge({ status }: JobStatusBadgeProps) {
  const statusConfig = {
    queued: {
      label: "Queued",
      variant: "secondary" as const,
      icon: Clock,
    },
    processing: {
      label: "Processing",
      variant: "default" as const,
      icon: Loader2,
    },
    completed: {
      label: "Completed",
      variant: "default" as const,
      icon: CheckCircle2,
    },
    failed: {
      label: "Failed",
      variant: "destructive" as const,
      icon: XCircle,
    },
    cancelled: {
      label: "Cancelled",
      variant: "outline" as const,
      icon: Ban,
    },
  };

  const config = statusConfig[status];
  const Icon = config.icon;

  return (
    <Badge variant={config.variant} className="flex items-center gap-1 w-fit">
      <Icon className="w-3 h-3" />
      {config.label}
    </Badge>
  );
}
