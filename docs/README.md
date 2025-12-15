# MP3 Extractor Documentation

Complete documentation for the MP3 Extractor Web Application.

---

## 🎯 Start Here

**New user?** → [Setup Guide](SETUP.md)
**Need help?** → [Quick Reference](QUICK_REFERENCE.md)
**Developer?** → [Development Guide](DEVELOPMENT.md)
**Using API?** → [API Documentation](API.md)

---

## 📚 Documentation Index

### Getting Started
- **[Setup Guide](SETUP.md)** - Installation and initial setup
- **[User Guide](USER_GUIDE.md)** - How to use the application
- **[Quick Reference](QUICK_REFERENCE.md)** - Cheat sheet for common tasks ⚡

### Technical Documentation
- **[API Documentation](API.md)** - Complete REST API reference
- **[Development Guide](DEVELOPMENT.md)** - For developers and contributors

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 20.9.0+
- ffmpeg

### Installation

```bash
# Install dependencies
make install

# Start the application
./dev.sh
```

Access at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📖 What's What

### For Users

If you want to **use** the application:

1. Start with **[Setup Guide](SETUP.md)** to install everything
2. Read **[User Guide](USER_GUIDE.md)** to learn how to convert videos

### For Developers

If you want to **develop** or **extend** the application:

1. Start with **[Setup Guide](SETUP.md)** to set up your environment
2. Read **[Development Guide](DEVELOPMENT.md)** for architecture and coding guidelines
3. Check **[API Documentation](API.md)** for endpoint details

### For API Integration

If you want to **integrate** with the API:

1. See **[API Documentation](API.md)** for complete endpoint reference
2. Check the interactive docs at http://localhost:8000/docs

## 🎯 Overview

MP3 Extractor is a modern web application for converting MP4 video files to MP3 audio files.

### Features

✅ **Modern Web UI** - Beautiful, responsive interface built with Next.js and shadcn/ui
✅ **Drag & Drop Upload** - Easy file selection with drag-and-drop support
✅ **Batch Processing** - Convert multiple files simultaneously (up to 3 parallel)
✅ **Real-time Progress** - Live progress updates via Server-Sent Events
✅ **Quality Settings** - Configure bitrate, sample rate, and metadata preservation
✅ **Job History** - View and manage all your conversion jobs
✅ **Download Options** - Download individual files or batch as ZIP
✅ **Automatic Cleanup** - Old files cleaned up after 7 days
✅ **Dark Mode** - Full dark mode support

### Tech Stack

**Frontend:**
- Next.js 14 (React App Router)
- shadcn/ui (Radix UI + Tailwind CSS)
- TypeScript
- Server-Sent Events (SSE)

**Backend:**
- FastAPI (async Python)
- SQLAlchemy ORM
- SQLite database
- ffmpeg for audio conversion

## 📁 Project Structure

```
mp3extractor/
├── backend/              # FastAPI backend
│   ├── api/             # API routes
│   ├── services/        # Business logic
│   └── models.py        # Database models
│
├── frontend/            # Next.js frontend
│   ├── app/            # Pages (App Router)
│   ├── components/     # React components
│   ├── hooks/          # Custom hooks
│   └── lib/            # Utilities
│
├── storage/            # File storage
│   ├── uploads/        # Uploaded MP4s
│   └── outputs/        # Converted MP3s
│
├── data/               # SQLite database
├── docs/               # Documentation (you are here!)
├── dev.sh             # Startup script
└── Makefile           # Make commands
```

## 🛠️ Common Tasks

### Start the Application

```bash
# Option 1: Shell script
./dev.sh

# Option 2: Make command
make dev

# Option 3: Aliases (after setup)
mp3dev
```

### Stop the Application

```bash
# Option 1: Press Ctrl+C in the terminal

# Option 2: Make command
make stop

# Option 3: Alias
mp3stop
```

### View Logs

```bash
# Backend logs
tail -f backend.log

# Frontend logs
tail -f frontend.log

# Alias
mp3logs
```

### Clean Up

```bash
# Remove logs and cache
make clean

# Alias
mp3clean
```

### Install Dependencies

```bash
# Install all
make install

# Backend only
pip install -r backend_requirements.txt

# Frontend only
cd frontend && npm install
```

## 🔧 Configuration

### Backend Configuration

Create `.env` file (optional, has defaults):

```env
DATABASE_URL=sqlite:///./data/jobs.db
STORAGE_PATH=./storage
MAX_UPLOAD_SIZE=524288000  # 500MB
FILE_RETENTION_DAYS=7
```

### Frontend Configuration

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 Architecture

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

1. **Upload** → Files stored in `storage/uploads/`, job created in database
2. **Convert** → Backend processes files with ffmpeg, sends progress via SSE
3. **Progress** → Frontend receives real-time updates and displays progress
4. **Download** → Files served from `storage/outputs/`

## 🎨 UI Features

### Home Page

- **File Upload Zone** - Drag-and-drop or click to browse
- **File List** - See selected files before conversion
- **Configuration Panel** - Quality presets and custom settings
- **Progress View** - Real-time conversion progress
- **Download Buttons** - Individual or batch download

### History Page

- **Job Table** - All conversion jobs with details
- **Status Filters** - Filter by job status
- **Pagination** - Navigate through job history
- **Actions** - Re-download or delete jobs

## 🔌 API Endpoints

Quick reference (see [API.md](API.md) for complete details):

**Files:**
- `POST /api/v1/files/upload` - Upload MP4 files
- `GET /api/v1/files/download/{job_id}/{filename}` - Download MP3
- `GET /api/v1/files/download-zip/{job_id}` - Download as ZIP

**Conversion:**
- `POST /api/v1/convert/start` - Start conversion
- `GET /api/v1/convert/status/{job_id}` - Get status
- `GET /api/v1/progress/{job_id}` - SSE progress stream

**Jobs:**
- `GET /api/v1/jobs` - List all jobs
- `DELETE /api/v1/jobs/{job_id}` - Delete job

**Health:**
- `GET /api/health` - Health check

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
make stop
# Or manually: kill -9 $(lsof -ti:8000)
```

**Backend won't start:**
```bash
pip install -r backend_requirements.txt
mkdir -p storage/uploads storage/outputs data
```

**Frontend won't start:**
```bash
cd frontend
rm -rf node_modules .next
npm install
```

**ffmpeg not found:**
```bash
# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

See [Setup Guide](SETUP.md#troubleshooting) for more troubleshooting help.

## 📝 Examples

### Convert a Single File

1. Open http://localhost:3000
2. Drop an MP4 file
3. Select quality (320k recommended)
4. Click "Start Conversion"
5. Wait for completion
6. Click "Download"

### Batch Convert Multiple Files

1. Drop multiple MP4 files at once
2. Configure settings once (applies to all)
3. Click "Start Conversion"
4. Watch parallel processing (up to 3 at once)
5. Click "Download All (ZIP)" when done

### Using the API

```bash
# Upload
curl -X POST http://localhost:8000/api/v1/files/upload \
  -F "files=@video.mp4"

# Convert
curl -X POST http://localhost:8000/api/v1/convert/start \
  -H "Content-Type: application/json" \
  -d '{"job_id":"<job_id>","config":{"bitrate":"320k"}}'

# Download
curl -O http://localhost:8000/api/v1/files/download/<job_id>/video.mp3
```

See [API.md](API.md) for complete API examples.

## 🤝 Contributing

Contributions are welcome! Please read the [Development Guide](DEVELOPMENT.md) before contributing.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Areas for Contribution

- Additional audio formats (WAV, AAC, etc.)
- Video editing features (trim, crop)
- User authentication
- Job scheduling
- Cloud storage integration
- Mobile app
- Docker support

## 📄 License

[Your license here]

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Next.js](https://nextjs.org/) - React framework
- [shadcn/ui](https://ui.shadcn.com/) - Beautiful UI components
- [ffmpeg](https://ffmpeg.org/) - Audio/video processing

## 📧 Support

For questions or issues:

1. Check the documentation in this folder
2. Review the interactive API docs at http://localhost:8000/docs
3. Check logs in `backend.log` and `frontend.log`

## 🗺️ Roadmap

**Current Version: 1.0.0**

**Planned Features:**
- [ ] User authentication and multi-user support
- [ ] Cloud deployment guide
- [ ] Docker containerization
- [ ] Additional output formats (WAV, AAC, OGG)
- [ ] Video trimming before conversion
- [ ] Queue management and prioritization
- [ ] Email notifications on completion
- [ ] API rate limiting
- [ ] Unit and integration tests
- [ ] Prometheus metrics
- [ ] Mobile-responsive improvements

## 📚 Additional Resources

### External Links

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Next.js Documentation**: https://nextjs.org/docs
- **shadcn/ui Components**: https://ui.shadcn.com/
- **Tailwind CSS**: https://tailwindcss.com/
- **ffmpeg Documentation**: https://ffmpeg.org/documentation.html

### Helpful Commands

```bash
# Check versions
python3 --version
node --version
ffmpeg -version

# Database access
sqlite3 data/jobs.db

# Check running processes
ps aux | grep uvicorn
ps aux | grep next

# Check ports
lsof -ti:8000
lsof -ti:3000

# Disk usage
du -sh storage/
du -sh data/
```

---

**Ready to get started?** Begin with the [Setup Guide](SETUP.md)!
