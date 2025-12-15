/**
 * SSE Client - Server-Sent Events connection manager
 */

import type {
  SSEEventType,
  SSEEventData,
  FileProgressEvent,
  FileCompletedEvent,
  JobCompletedEvent,
  ErrorEvent,
} from "@/types/job";

export type SSEEventHandler = (eventType: SSEEventType, data: SSEEventData) => void;

export class SSEClient {
  private eventSource: EventSource | null = null;
  private jobId: string;
  private baseURL: string;
  private handlers: SSEEventHandler[] = [];
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout: NodeJS.Timeout | null = null;

  constructor(jobId: string) {
    this.jobId = jobId;
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  }

  /**
   * Connect to SSE endpoint
   */
  connect(): void {
    if (this.eventSource) {
      this.disconnect();
    }

    const url = `${this.baseURL}/api/v1/progress/${this.jobId}`;
    this.eventSource = new EventSource(url);

    // Connected event
    this.eventSource.addEventListener("connected", (event) => {
      this.reconnectAttempts = 0;
      const data = JSON.parse(event.data);
      this.notifyHandlers("connected", data);
    });

    // File progress event
    this.eventSource.addEventListener("file_progress", (event) => {
      const data = JSON.parse(event.data) as FileProgressEvent;
      this.notifyHandlers("file_progress", data);
    });

    // File completed event
    this.eventSource.addEventListener("file_completed", (event) => {
      const data = JSON.parse(event.data) as FileCompletedEvent;
      this.notifyHandlers("file_completed", data);
    });

    // Job completed event
    this.eventSource.addEventListener("job_completed", (event) => {
      const data = JSON.parse(event.data) as JobCompletedEvent;
      this.notifyHandlers("job_completed", data);
      // Automatically disconnect after job completion
      setTimeout(() => this.disconnect(), 1000);
    });

    // Error event
    this.eventSource.addEventListener("error", (event: Event) => {
      if (event.type === "error") {
        // Try to parse error data if available
        try {
          const messageEvent = event as MessageEvent;
          if (messageEvent.data) {
            const data = JSON.parse(messageEvent.data) as ErrorEvent;
            this.notifyHandlers("error", data);
          }
        } catch (e) {
          // Connection error
          this.handleConnectionError();
        }
      }
    });

    // Connection error (generic)
    this.eventSource.onerror = () => {
      this.handleConnectionError();
    };
  }

  /**
   * Handle connection errors with retry logic
   */
  private handleConnectionError(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);

      console.log(
        `SSE connection lost. Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`
      );

      this.reconnectTimeout = setTimeout(() => {
        this.connect();
      }, delay);
    } else {
      console.error("SSE connection failed after maximum retry attempts");
      this.disconnect();
    }
  }

  /**
   * Disconnect from SSE endpoint
   */
  disconnect(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }

    this.reconnectAttempts = 0;
  }

  /**
   * Add event handler
   */
  onEvent(handler: SSEEventHandler): () => void {
    this.handlers.push(handler);

    // Return unsubscribe function
    return () => {
      this.handlers = this.handlers.filter((h) => h !== handler);
    };
  }

  /**
   * Notify all handlers
   */
  private notifyHandlers(eventType: SSEEventType, data: SSEEventData): void {
    this.handlers.forEach((handler) => {
      try {
        handler(eventType, data);
      } catch (error) {
        console.error("Error in SSE event handler:", error);
      }
    });
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.eventSource !== null && this.eventSource.readyState === EventSource.OPEN;
  }
}
