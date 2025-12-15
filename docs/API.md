# API Documentation

Complete REST API reference for the MP3 Extractor backend.

## Base URL

```
http://localhost:8000
```

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Authentication

Currently, no authentication is required (local use only).

## Error Handling

All endpoints return standard HTTP status codes:

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Endpoints

### Health & Info

#### GET `/api/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected"
}
```

#### GET `/`

API information.

**Response:**
```json
{
  "name": "MP3 Extractor API",
  "version": "1.0.0",
  "description": "Convert MP4 videos to MP3 audio files",
  "docs": "/docs"
}
```

---

## File Management

### POST `/api/v1/files/upload`

Upload MP4 files for conversion.

**Content-Type:** `multipart/form-data`

**Parameters:**
- `files`: File[] (required) - One or more MP4 files

**Example (curl):**
```bash
curl -X POST "http://localhost:8000/api/v1/files/upload" \
  -F "files=@video1.mp4" \
  -F "files=@video2.mp4"
```

**Example (JavaScript):**
```javascript
const formData = new FormData();
formData.append('files', file1);
formData.append('files', file2);

const response = await fetch('http://localhost:8000/api/v1/files/upload', {
  method: 'POST',
  body: formData
});

const data = await response.json();
```

**Response (200 OK):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "files_uploaded": 2,
  "filenames": ["video1.mp4", "video2.mp4"]
}
```

---

### GET `/api/v1/files/download/{job_id}/{filename}`

Download a single converted MP3 file.

**Parameters:**
- `job_id`: string (path) - Job UUID
- `filename`: string (path) - MP3 filename (e.g., "video1.mp3")

**Example:**
```bash
curl -O "http://localhost:8000/api/v1/files/download/550e8400-e29b-41d4-a716-446655440000/video1.mp3"
```

**Response:** Binary MP3 file
**Content-Type:** `audio/mpeg`
**Content-Disposition:** `attachment; filename="video1.mp3"`

---

### GET `/api/v1/files/download-zip/{job_id}`

Download all converted files as a ZIP archive.

**Parameters:**
- `job_id`: string (path) - Job UUID

**Example:**
```bash
curl -O "http://localhost:8000/api/v1/files/download-zip/550e8400-e29b-41d4-a716-446655440000"
```

**Response:** Binary ZIP file
**Content-Type:** `application/zip`
**Content-Disposition:** `attachment; filename="mp3_conversion_{job_id}.zip"`

---

### DELETE `/api/v1/files/cleanup/{job_id}`

Manually delete all files for a job (usually automatic after 7 days).

**Parameters:**
- `job_id`: string (path) - Job UUID

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/files/cleanup/550e8400-e29b-41d4-a716-446655440000"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Files cleaned up successfully",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### GET `/api/v1/files/disk-usage/{job_id}`

Get disk space usage for a job.

**Parameters:**
- `job_id`: string (path) - Job UUID

**Response (200 OK):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "input_size_bytes": 104857600,
  "output_size_bytes": 8388608,
  "total_size_bytes": 113246208,
  "input_size_mb": 100.0,
  "output_size_mb": 8.0,
  "total_size_mb": 108.0
}
```

---

## Conversion

### POST `/api/v1/convert/start`

Start converting uploaded files.

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "config": {
    "bitrate": "320k",
    "sample_rate": 48000,
    "preserve_metadata": true
  }
}
```

**Fields:**
- `job_id`: string (required) - Job UUID from upload
- `config.bitrate`: string (required) - Audio bitrate (128k - 320k)
- `config.sample_rate`: integer | null (optional) - Sample rate in Hz (44100, 48000) or null for auto
- `config.preserve_metadata`: boolean (optional, default: true) - Preserve metadata

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/convert/start" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "config": {
      "bitrate": "320k",
      "sample_rate": null,
      "preserve_metadata": true
    }
  }'
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Conversion started",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### GET `/api/v1/convert/status/{job_id}`

Get current conversion status.

**Parameters:**
- `job_id`: string (path) - Job UUID

**Example:**
```bash
curl "http://localhost:8000/api/v1/convert/status/550e8400-e29b-41d4-a716-446655440000"
```

**Response (200 OK):**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "created_at": "2025-12-15T13:30:00Z",
  "updated_at": "2025-12-15T13:30:45Z",
  "started_at": "2025-12-15T13:30:05Z",
  "completed_at": null,
  "bitrate": "320k",
  "sample_rate": 48000,
  "preserve_metadata": true,
  "total_files": 2,
  "completed_files": 1,
  "failed_files": 0,
  "overall_progress": 0.5,
  "error_message": null,
  "output_path": "storage/outputs/550e8400-e29b-41d4-a716-446655440000",
  "files": [
    {
      "input_filename": "video1.mp4",
      "output_filename": "video1.mp3",
      "status": "completed",
      "progress": 1.0,
      "output_size": 8388608,
      "error_message": null
    },
    {
      "input_filename": "video2.mp4",
      "output_filename": "video2.mp3",
      "status": "processing",
      "progress": 0.45,
      "output_size": null,
      "error_message": null
    }
  ]
}
```

---

### DELETE `/api/v1/convert/cancel/{job_id}`

Cancel an in-progress conversion.

**Parameters:**
- `job_id`: string (path) - Job UUID

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/convert/cancel/550e8400-e29b-41d4-a716-446655440000"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Conversion cancelled",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### GET `/api/v1/progress/{job_id}` (SSE)

Server-Sent Events stream for real-time progress updates.

**Parameters:**
- `job_id`: string (path) - Job UUID

**Content-Type:** `text/event-stream`

**Example (curl):**
```bash
curl -N "http://localhost:8000/api/v1/progress/550e8400-e29b-41d4-a716-446655440000"
```

**Example (JavaScript):**
```javascript
const eventSource = new EventSource(
  `http://localhost:8000/api/v1/progress/${jobId}`
);

eventSource.addEventListener('connected', (e) => {
  const data = JSON.parse(e.data);
  console.log('Connected:', data);
});

eventSource.addEventListener('file_progress', (e) => {
  const data = JSON.parse(e.data);
  console.log(`File ${data.filename}: ${data.progress * 100}%`);
});

eventSource.addEventListener('file_completed', (e) => {
  const data = JSON.parse(e.data);
  console.log(`Completed: ${data.filename} -> ${data.output_filename}`);
});

eventSource.addEventListener('job_completed', (e) => {
  const data = JSON.parse(e.data);
  console.log('Job completed:', data);
  eventSource.close();
});

eventSource.addEventListener('error', (e) => {
  const data = JSON.parse(e.data);
  console.error('Error:', data);
});
```

**Event Types:**

#### `connected`
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Connected to progress stream"
}
```

#### `file_progress`
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "video1.mp4",
  "progress": 0.45,
  "current_ms": 45000,
  "total_ms": 100000
}
```

#### `file_completed`
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "video1.mp4",
  "output_filename": "video1.mp3",
  "output_size": 8388608
}
```

#### `job_completed`
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "total_files": 2,
  "completed_files": 2,
  "failed_files": 0
}
```

#### `error`
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "video2.mp4",
  "error": "Failed to convert file: Invalid format"
}
```

---

## Job Management

### GET `/api/v1/jobs`

List all jobs with pagination and filtering.

**Query Parameters:**
- `page`: integer (optional, default: 1) - Page number
- `page_size`: integer (optional, default: 20) - Items per page
- `status`: string (optional) - Filter by status (queued, processing, completed, failed, cancelled)

**Example:**
```bash
curl "http://localhost:8000/api/v1/jobs?page=1&page_size=10&status=completed"
```

**Response (200 OK):**
```json
{
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "created_at": "2025-12-15T13:30:00Z",
      "completed_at": "2025-12-15T13:32:15Z",
      "bitrate": "320k",
      "sample_rate": 48000,
      "preserve_metadata": true,
      "total_files": 2,
      "completed_files": 2,
      "failed_files": 0,
      "overall_progress": 1.0,
      "files": [
        {
          "input_filename": "video1.mp4",
          "output_filename": "video1.mp3",
          "status": "completed",
          "progress": 1.0,
          "output_size": 8388608
        }
      ]
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 10,
  "total_pages": 2
}
```

---

### GET `/api/v1/jobs/{job_id}`

Get details of a specific job.

**Parameters:**
- `job_id`: string (path) - Job UUID

**Example:**
```bash
curl "http://localhost:8000/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000"
```

**Response (200 OK):**
Same format as status endpoint (see `/api/v1/convert/status/{job_id}`).

---

### DELETE `/api/v1/jobs/{job_id}`

Delete a job and all associated files.

**Parameters:**
- `job_id`: string (path) - Job UUID

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Job deleted successfully",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### POST `/api/v1/jobs/clear-history`

Delete all jobs older than specified days.

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "days_old": 7
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/jobs/clear-history" \
  -H "Content-Type: application/json" \
  -d '{"days_old": 7}'
```

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Cleared 5 old jobs",
  "deleted_count": 5
}
```

---

## Data Models

### ConversionConfig

```typescript
{
  bitrate: string;           // "128k" | "160k" | "192k" | "256k" | "320k"
  sample_rate: number | null; // 44100 | 48000 | null (auto)
  preserve_metadata: boolean; // true | false
}
```

### JobStatus

```typescript
type JobStatus =
  | "queued"      // Created, waiting to start
  | "processing"  // Currently converting
  | "completed"   // All files done
  | "failed"      // Job failed
  | "cancelled";  // User cancelled
```

### FileStatus

```typescript
type FileStatus =
  | "pending"     // Waiting to start
  | "processing"  // Currently converting
  | "completed"   // Successfully converted
  | "failed";     // Conversion failed
```

---

## Rate Limiting

Currently no rate limiting is implemented (local use only).

## CORS

CORS is enabled for `http://localhost:3000` by default.

To modify CORS settings, edit `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your origins here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Complete Workflow Example

### 1. Upload Files

```bash
UPLOAD_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/files/upload" \
  -F "files=@video1.mp4" \
  -F "files=@video2.mp4")

JOB_ID=$(echo $UPLOAD_RESPONSE | jq -r '.job_id')
echo "Job ID: $JOB_ID"
```

### 2. Start Conversion

```bash
curl -X POST "http://localhost:8000/api/v1/convert/start" \
  -H "Content-Type: application/json" \
  -d "{
    \"job_id\": \"$JOB_ID\",
    \"config\": {
      \"bitrate\": \"320k\",
      \"sample_rate\": null,
      \"preserve_metadata\": true
    }
  }"
```

### 3. Monitor Progress (SSE)

```bash
curl -N "http://localhost:8000/api/v1/progress/$JOB_ID"
```

### 4. Check Status

```bash
curl "http://localhost:8000/api/v1/convert/status/$JOB_ID"
```

### 5. Download Files

```bash
# Download single file
curl -O "http://localhost:8000/api/v1/files/download/$JOB_ID/video1.mp3"

# Download all as ZIP
curl -O "http://localhost:8000/api/v1/files/download-zip/$JOB_ID"
```

### 6. Cleanup

```bash
curl -X DELETE "http://localhost:8000/api/v1/jobs/$JOB_ID"
```

---

## WebSocket Alternative (Not Implemented)

Currently using Server-Sent Events (SSE). If WebSocket support is needed in the future, it can be added with FastAPI's WebSocket support.
