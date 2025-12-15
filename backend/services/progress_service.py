"""
Server-Sent Events (SSE) progress service
"""

import asyncio
import json
from typing import Dict, Set
from fastapi import Request
from fastapi.responses import StreamingResponse


class ProgressService:
    """
    Manages SSE connections and broadcasts progress updates
    """

    def __init__(self):
        # Track active SSE connections per job
        self.connections: Dict[str, Set[asyncio.Queue]] = {}

    def add_connection(self, job_id: str, queue: asyncio.Queue):
        """Add a new SSE connection for a job"""
        if job_id not in self.connections:
            self.connections[job_id] = set()
        self.connections[job_id].add(queue)

    def remove_connection(self, job_id: str, queue: asyncio.Queue):
        """Remove an SSE connection"""
        if job_id in self.connections:
            self.connections[job_id].discard(queue)
            if not self.connections[job_id]:
                del self.connections[job_id]

    async def broadcast(self, job_id: str, event: str, data: dict):
        """
        Broadcast an event to all connections for a job

        Args:
            job_id: Job ID
            event: Event type (file_progress, file_completed, job_completed, error)
            data: Event data
        """
        if job_id not in self.connections:
            return

        # Create SSE message
        message = f"event: {event}\ndata: {json.dumps(data)}\n\n"

        # Send to all connections
        dead_queues = []
        for queue in self.connections[job_id]:
            try:
                await queue.put(message)
            except:
                dead_queues.append(queue)

        # Remove dead connections
        for queue in dead_queues:
            self.remove_connection(job_id, queue)

    async def stream_progress(self, job_id: str, request: Request):
        """
        Create SSE stream for a job

        Args:
            job_id: Job ID
            request: FastAPI request (for disconnect detection)

        Returns:
            StreamingResponse with SSE events
        """
        queue = asyncio.Queue()
        self.add_connection(job_id, queue)

        async def event_generator():
            try:
                # Send initial connection message
                yield f"event: connected\ndata: {json.dumps({'job_id': job_id})}\n\n"

                while True:
                    # Check if client disconnected
                    if await request.is_disconnected():
                        break

                    # Wait for new events (with timeout)
                    try:
                        message = await asyncio.wait_for(queue.get(), timeout=30.0)
                        yield message
                    except asyncio.TimeoutError:
                        # Send keep-alive ping
                        yield f": keepalive\n\n"

            except asyncio.CancelledError:
                pass
            finally:
                # Clean up connection
                self.remove_connection(job_id, queue)

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )


# Global progress service instance
progress_service = ProgressService()
