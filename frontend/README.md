# MP3 Extractor Frontend

Modern web interface for MP4 to MP3 conversion, built with Next.js 14 and shadcn/ui.

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **State Management**: React Hooks
- **API Client**: Axios
- **Real-time**: Server-Sent Events (SSE)
- **Utilities**: date-fns, lucide-react

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running at http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser.

## Project Structure

```
frontend/
├── app/                      # Next.js App Router
│   ├── layout.tsx           # Root layout with navigation
│   ├── page.tsx             # Home/conversion page
│   ├── not-found.tsx        # 404 error page
│   └── history/
│       └── page.tsx         # Job history page
│
├── components/              # React components
│   ├── ui/                  # shadcn/ui primitives
│   ├── conversion/          # Conversion UI components
│   ├── config/              # Configuration components
│   └── history/             # History page components
│
├── hooks/                   # Custom React hooks
│   ├── use-conversion.ts    # Upload & conversion logic
│   ├── use-progress.ts      # SSE progress tracking
│   └── use-jobs.ts          # Job management
│
├── lib/                     # Utilities and clients
│   ├── api-client.ts        # Type-safe API client
│   ├── sse-client.ts        # SSE connection manager
│   └── utils.ts             # Helper functions
│
└── types/                   # TypeScript types
    ├── api.ts               # API request/response types
    └── job.ts               # Job and file types
```

## Features

### Home Page (/)
- Drag-and-drop file upload
- Multi-file batch conversion
- Configuration panel with quality presets
- Real-time progress tracking
- Individual and batch file downloads

### History Page (/history)
- Job list with status badges
- Filter by status
- Pagination
- Re-download completed jobs
- Delete individual jobs
- Clear old jobs (7+ days)

## Available Scripts

```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start

# Linting
npm run lint
```

## Custom Hooks

### useConversion
Manages the upload and conversion flow:
```typescript
const { state, jobId, uploadFiles, reset } = useConversion();
```

### useProgress
Tracks real-time progress via SSE:
```typescript
const { connected, filesProgress, completedFiles, overallProgress } = useProgress(jobId);
```

### useJobs
Manages job history and operations:
```typescript
const { jobs, loading, fetchJobs, deleteJob, clearHistory } = useJobs();
```

## Troubleshooting

### Development Server Issues
```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### API Connection Issues
- Verify backend is running at http://localhost:8000
- Check CORS settings in backend allow http://localhost:3000
- Confirm `.env.local` has correct `NEXT_PUBLIC_API_URL`

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Main Project Documentation](../README_WEB.md)
