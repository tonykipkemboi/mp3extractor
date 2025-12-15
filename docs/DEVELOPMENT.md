# Development Guide

Guide for developers contributing to or extending the MP3 Extractor project.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Backend Development](#backend-development)
- [Frontend Development](#frontend-development)
- [Database](#database)
- [Testing](#testing)
- [Code Style](#code-style)
- [Contributing](#contributing)

## Architecture Overview

### Tech Stack

**Backend:**
- **Framework**: FastAPI (async Python web framework)
- **Database**: SQLite with SQLAlchemy ORM
- **Real-time**: Server-Sent Events (SSE)
- **Audio Processing**: ffmpeg via mp3extractor package

**Frontend:**
- **Framework**: Next.js 14 (React with App Router)
- **UI Library**: shadcn/ui (Radix UI + Tailwind CSS)
- **State Management**: React hooks
- **HTTP Client**: Axios
- **Real-time**: EventSource API (SSE)

### System Design

```
┌─────────────┐         ┌──────────────┐         ┌────────────┐
│   Browser   │ ◄─────► │   Next.js    │ ◄─────► │  FastAPI   │
│  (React UI) │  HTTP   │  (Frontend)  │   API   │  (Backend) │
└─────────────┘         └──────────────┘         └────────────┘
                                                         │
                               ┌─────────────────────────┼──────────┐
                               │                         │          │
                          ┌────▼─────┐         ┌────────▼───┐   ┌──▼──────┐
                          │ SQLite   │         │  Storage   │   │ ffmpeg  │
                          │ Database │         │ (uploads/  │   │ (Audio  │
                          │          │         │  outputs)  │   │ Process)│
                          └──────────┘         └────────────┘   └─────────┘
```

### Request Flow

1. **Upload**: User uploads MP4 → Frontend → Backend saves to storage → Creates job in DB
2. **Convert**: User clicks start → Backend spawns async conversion → Sends SSE progress
3. **Progress**: Frontend listens to SSE → Updates UI in real-time
4. **Download**: User downloads → Backend streams file from storage

## Development Setup

### Prerequisites

- Python 3.12+
- Node.js 25.2.1+
- ffmpeg
- Git

### Initial Setup

```bash
# Clone repository
git clone <repo-url>
cd mp3extractor

# Install dependencies
make install

# Create required directories
mkdir -p storage/uploads storage/outputs data

# Start development servers
make dev
```

### Development Environment

Create `.env` file:
```env
# Backend
DATABASE_URL=sqlite:///./data/jobs.db
STORAGE_PATH=./storage
MAX_UPLOAD_SIZE=524288000
FILE_RETENTION_DAYS=7
```

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
mp3extractor/
├── backend/                      # FastAPI Backend
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry point
│   ├── database.py               # SQLAlchemy setup
│   ├── models.py                 # Database models
│   ├── schemas.py                # Pydantic schemas
│   ├── api/                      # API routes
│   │   ├── files.py              # File upload/download
│   │   ├── jobs.py               # Job management
│   │   └── conversion.py         # Conversion endpoints
│   └── services/                 # Business logic
│       ├── file_service.py       # File operations
│       ├── job_service.py        # Job CRUD
│       ├── conversion_service.py # Conversion logic
│       └── progress_service.py   # SSE streaming
│
├── frontend/                     # Next.js Frontend
│   ├── app/                      # Next.js App Router
│   │   ├── layout.tsx            # Root layout
│   │   ├── page.tsx              # Home page
│   │   ├── globals.css           # Global styles
│   │   └── history/
│   │       └── page.tsx          # History page
│   ├── components/               # React components
│   │   ├── ui/                   # shadcn/ui components
│   │   ├── conversion/           # Conversion UI
│   │   ├── config/               # Settings UI
│   │   └── history/              # History UI
│   ├── hooks/                    # Custom React hooks
│   │   ├── use-conversion.ts
│   │   ├── use-progress.ts
│   │   └── use-jobs.ts
│   ├── lib/                      # Utilities
│   │   ├── api-client.ts         # API client
│   │   ├── sse-client.ts         # SSE client
│   │   └── utils.ts              # Helper functions
│   └── types/                    # TypeScript types
│       ├── api.ts
│       └── job.ts
│
├── storage/                      # File storage (gitignored)
│   ├── uploads/                  # Uploaded MP4s
│   └── outputs/                  # Converted MP3s
│
├── data/                         # Database (gitignored)
│   └── jobs.db
│
├── docs/                         # Documentation
│   ├── SETUP.md
│   ├── USER_GUIDE.md
│   ├── API.md
│   └── DEVELOPMENT.md (this file)
│
├── dev.sh                        # Development startup script
├── Makefile                      # Make commands
├── .aliases                      # Shell aliases
├── backend_requirements.txt      # Python dependencies
└── README.md                     # Main README
```

## Backend Development

### Running Backend Only

```bash
# With auto-reload
python3 -m uvicorn backend.main:app --reload --port 8000

# Or with Make
make backend
```

### Adding New Endpoints

1. **Define Pydantic Schema** (`backend/schemas.py`):
```python
from pydantic import BaseModel

class MyRequest(BaseModel):
    field: str

class MyResponse(BaseModel):
    result: str
```

2. **Add Endpoint** (`backend/api/my_endpoint.py`):
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import MyRequest, MyResponse

router = APIRouter(prefix="/api/v1/myendpoint", tags=["My Feature"])

@router.post("/action", response_model=MyResponse)
async def my_action(request: MyRequest, db: Session = Depends(get_db)):
    # Your logic here
    return MyResponse(result="success")
```

3. **Register Router** (`backend/main.py`):
```python
from .api import my_endpoint

app.include_router(my_endpoint.router)
```

### Database Models

Models are defined in `backend/models.py` using SQLAlchemy:

```python
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime
from .database import Base

class MyModel(Base):
    __tablename__ = "my_table"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
```

### Database Migrations

Currently using automatic table creation. For migrations:

```python
# In backend/database.py
Base.metadata.create_all(bind=engine)
```

For production, consider using Alembic for migrations.

### Adding Services

Services contain business logic in `backend/services/`:

```python
from sqlalchemy.orm import Session
from ..models import MyModel

class MyService:
    def __init__(self):
        pass

    def do_something(self, db: Session, param: str):
        # Business logic
        return result
```

### Testing Backend

```bash
# Start backend
python3 -m uvicorn backend.main:app --reload --port 8000

# Test endpoints
curl http://localhost:8000/api/health

# View API docs
open http://localhost:8000/docs
```

## Frontend Development

### Running Frontend Only

```bash
cd frontend
npm run dev

# Or with Make
make frontend
```

### Project Structure

Next.js 14 with App Router:
- `app/` - Pages and layouts
- `components/` - React components
- `hooks/` - Custom hooks
- `lib/` - Utilities and helpers
- `types/` - TypeScript definitions

### Adding Components

1. **Create Component** (`frontend/components/my-component.tsx`):
```tsx
"use client";

import { useState } from "react";

interface MyComponentProps {
  value: string;
  onChange: (value: string) => void;
}

export function MyComponent({ value, onChange }: MyComponentProps) {
  return (
    <div>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}
```

2. **Use Component**:
```tsx
import { MyComponent } from "@/components/my-component";

export default function Page() {
  const [value, setValue] = useState("");
  return <MyComponent value={value} onChange={setValue} />;
}
```

### Adding shadcn/ui Components

```bash
# List available components
npx shadcn-ui@latest add

# Add specific component
npx shadcn-ui@latest add button
```

### Custom Hooks

Create in `frontend/hooks/`:

```tsx
import { useState, useEffect } from "react";

export function useMyFeature() {
  const [data, setData] = useState(null);

  useEffect(() => {
    // Logic here
  }, []);

  return { data };
}
```

### API Client

Extend `frontend/lib/api-client.ts`:

```typescript
class ApiClient {
  // ... existing methods

  async myNewEndpoint(param: string): Promise<MyResponse> {
    const response = await this.client.post("/api/v1/myendpoint/action", {
      param
    });
    return response.data;
  }
}
```

### Styling

Using Tailwind CSS with custom utilities in `globals.css`:

```css
@layer utilities {
  .my-custom-class {
    @apply bg-gradient-to-r from-blue-500 to-purple-500;
  }
}
```

### TypeScript Types

Define in `frontend/types/`:

```typescript
export interface MyType {
  id: string;
  name: string;
  createdAt: string;
}
```

## Database

### Schema

**Jobs Table:**
```sql
CREATE TABLE jobs (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    bitrate TEXT,
    sample_rate INTEGER,
    preserve_metadata BOOLEAN,
    total_files INTEGER,
    completed_files INTEGER,
    failed_files INTEGER,
    overall_progress REAL,
    error_message TEXT,
    output_path TEXT
);
```

**Job Files Table:**
```sql
CREATE TABLE job_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    input_filename TEXT NOT NULL,
    output_filename TEXT,
    status TEXT NOT NULL,
    file_size INTEGER,
    output_size INTEGER,
    progress REAL,
    duration_seconds REAL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);
```

### Accessing Database

```bash
# SQLite CLI
sqlite3 data/jobs.db

# View tables
.tables

# View schema
.schema jobs

# Query data
SELECT * FROM jobs LIMIT 5;
```

### Resetting Database

```bash
# WARNING: Deletes all data
rm data/jobs.db

# Restart backend to recreate
python3 -m uvicorn backend.main:app --reload --port 8000
```

## Testing

### Manual Testing

**Backend:**
```bash
# Health check
curl http://localhost:8000/api/health

# Upload test
curl -X POST http://localhost:8000/api/v1/files/upload \
  -F "files=@test.mp4"

# View interactive docs
open http://localhost:8000/docs
```

**Frontend:**
```bash
# Start dev server
npm run dev

# Open in browser
open http://localhost:3000

# Check console for errors
# Use React DevTools
```

### Unit Tests (Future)

For future implementation:

**Backend (pytest):**
```bash
pip install pytest pytest-asyncio
pytest backend/tests/
```

**Frontend (Jest + React Testing Library):**
```bash
npm install --save-dev jest @testing-library/react
npm test
```

## Code Style

### Backend (Python)

- **Style**: PEP 8
- **Docstrings**: Google style
- **Type hints**: Use for function signatures

```python
from typing import List, Optional

def my_function(param: str, optional: Optional[int] = None) -> List[str]:
    """
    Brief description.

    Args:
        param: Description of param
        optional: Description of optional param

    Returns:
        List of results
    """
    return []
```

### Frontend (TypeScript)

- **Style**: Prettier + ESLint
- **Components**: Functional components with hooks
- **Naming**: PascalCase for components, camelCase for functions

```typescript
interface Props {
  value: string;
  onChange: (value: string) => void;
}

export function MyComponent({ value, onChange }: Props) {
  const handleChange = (newValue: string) => {
    onChange(newValue);
  };

  return <div />;
}
```

### Formatting

**Backend:**
```bash
# Format with black
pip install black
black backend/

# Sort imports
pip install isort
isort backend/
```

**Frontend:**
```bash
# Format with prettier
npm install --save-dev prettier
npx prettier --write "**/*.{ts,tsx,js,jsx,json,css}"

# Lint
npm run lint
```

## Contributing

### Workflow

1. **Create feature branch**:
```bash
git checkout -b feature/my-feature
```

2. **Make changes** and test locally

3. **Commit with clear message**:
```bash
git commit -m "feat: add new feature"
```

4. **Push and create PR**:
```bash
git push origin feature/my-feature
```

### Commit Messages

Follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code restructure
- `test:` Tests
- `chore:` Maintenance

### Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No console errors
- [ ] Tested manually
- [ ] PR description is clear

## Debugging

### Backend Debugging

```python
# Add breakpoint
import pdb; pdb.set_trace()

# View logs
tail -f backend.log

# Enable debug mode
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Frontend Debugging

```typescript
// Console logging
console.log('Debug:', value);

// React DevTools
// Install Chrome extension

// Network tab
// Check API requests/responses
```

## Performance

### Backend Optimization

- Use async/await for I/O operations
- Limit concurrent conversions (semaphore)
- Throttle progress updates
- Index database queries

### Frontend Optimization

- Use React.memo for expensive components
- Implement virtual scrolling for large lists
- Lazy load routes
- Optimize images

## Security Considerations

### Current Implementation (Local Use)

- No authentication (localhost only)
- No rate limiting
- No input sanitization beyond file type

### For Production Deployment

Would need:
- User authentication (JWT, OAuth)
- Rate limiting (per user/IP)
- Input validation and sanitization
- HTTPS/TLS
- CSRF protection
- File upload limits and validation
- Security headers

## Deployment

### Docker (Future)

```dockerfile
# Example Dockerfile
FROM python:3.12
WORKDIR /app
COPY backend_requirements.txt .
RUN pip install -r backend_requirements.txt
COPY backend ./backend
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0"]
```

### Production Checklist

- [ ] Set production environment variables
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS
- [ ] Add authentication
- [ ] Configure CORS properly
- [ ] Set up monitoring
- [ ] Configure backup strategy
- [ ] Add rate limiting
- [ ] Security audit

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui](https://ui.shadcn.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Tailwind CSS](https://tailwindcss.com/)
