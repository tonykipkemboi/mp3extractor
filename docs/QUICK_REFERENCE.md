# Quick Reference

Fast lookup for common commands and operations.

## 🚀 Starting & Stopping

```bash
# Start both servers
./dev.sh                  # Shell script
make dev                  # Make command
mp3dev                    # Alias (after setup)

# Start individually
make backend              # Backend only
make frontend             # Frontend only

# Stop everything
Ctrl+C                    # In terminal
make stop                 # Kill all processes
mp3stop                   # Alias
```

## 🌐 URLs

```
Frontend:       http://localhost:3000
Backend API:    http://localhost:8000
API Docs:       http://localhost:8000/docs
ReDoc:          http://localhost:8000/redoc
Health Check:   http://localhost:8000/api/health
Job History:    http://localhost:3000/history
```

## 📦 Installation

```bash
# Everything
make install

# Backend only
pip install -r backend_requirements.txt

# Frontend only
cd frontend && npm install
```

## 🔧 Maintenance

```bash
# View logs
tail -f backend.log       # Backend logs
tail -f frontend.log      # Frontend logs
mp3logs                   # Frontend logs (alias)

# Clean up
make clean                # Remove logs and cache
mp3clean                  # Alias
rm -rf frontend/.next     # Clear Next.js cache
rm data/jobs.db           # Reset database (WARNING)

# Check running processes
ps aux | grep uvicorn     # Backend process
ps aux | grep next        # Frontend process
lsof -ti:8000             # What's on port 8000
lsof -ti:3000             # What's on port 3000
```

## 🐛 Troubleshooting

```bash
# Port already in use
kill -9 $(lsof -ti:8000)
kill -9 $(lsof -ti:3000)

# Backend issues
pip install -r backend_requirements.txt
python3 -m uvicorn backend.main:app --reload --port 8000

# Frontend issues
cd frontend
rm -rf node_modules .next
npm install
npm run dev

# ffmpeg not found
brew install ffmpeg       # macOS
sudo apt install ffmpeg   # Linux

# Permission errors
chmod +x dev.sh
chmod -R 755 storage data
```

## 📝 Web UI Operations

### Upload Files
1. Drag MP4 to upload zone, OR
2. Click upload zone → Select files

### Configure Settings
- **Low**: 128k bitrate (small files)
- **Medium**: 192k bitrate (balanced)
- **High**: 256k bitrate (good quality)
- **Custom**: 320k bitrate (best quality)

### Convert
1. Upload files
2. Choose quality
3. Click "Start Conversion"
4. Wait for progress to complete

### Download
- **Single file**: Click download button on file
- **All files**: Click "Download All (ZIP)"

### History
1. Go to http://localhost:3000/history
2. View all past jobs
3. Re-download or delete jobs

## 🔌 API Quick Reference

### Upload
```bash
curl -X POST http://localhost:8000/api/v1/files/upload \
  -F "files=@video.mp4"
```

### Convert
```bash
curl -X POST http://localhost:8000/api/v1/convert/start \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "YOUR_JOB_ID",
    "config": {
      "bitrate": "320k",
      "sample_rate": null,
      "preserve_metadata": true
    }
  }'
```

### Status
```bash
curl http://localhost:8000/api/v1/convert/status/YOUR_JOB_ID
```

### Download
```bash
# Single file
curl -O http://localhost:8000/api/v1/files/download/JOB_ID/file.mp3

# ZIP
curl -O http://localhost:8000/api/v1/files/download-zip/JOB_ID
```

### List Jobs
```bash
curl http://localhost:8000/api/v1/jobs?page=1&page_size=20
```

### Delete Job
```bash
curl -X DELETE http://localhost:8000/api/v1/jobs/JOB_ID
```

## 🗄️ Database

```bash
# Access database
sqlite3 data/jobs.db

# Common queries
.tables                           # List tables
.schema jobs                      # View schema
SELECT * FROM jobs LIMIT 5;       # View jobs
SELECT * FROM job_files LIMIT 5;  # View files
DELETE FROM jobs WHERE status='failed';  # Delete failed jobs
.quit                             # Exit

# Reset database (WARNING: deletes all data)
rm data/jobs.db
# Restart backend to recreate
```

## 📂 File Locations

```
Backend:        /Users/tonykipkemboi/mp3extractor/backend/
Frontend:       /Users/tonykipkemboi/mp3extractor/frontend/
Uploads:        /Users/tonykipkemboi/mp3extractor/storage/uploads/
Outputs:        /Users/tonykipkemboi/mp3extractor/storage/outputs/
Database:       /Users/tonykipkemboi/mp3extractor/data/jobs.db
Backend Log:    /Users/tonykipkemboi/mp3extractor/backend.log
Frontend Log:   /Users/tonykipkemboi/mp3extractor/frontend.log
```

## 🔑 Environment Variables

### Backend (.env)
```env
DATABASE_URL=sqlite:///./data/jobs.db
STORAGE_PATH=./storage
MAX_UPLOAD_SIZE=524288000  # 500MB
FILE_RETENTION_DAYS=7
```

### Frontend (frontend/.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🎨 Quality Settings

| Setting | Bitrate | File Size | Use Case |
|---------|---------|-----------|----------|
| **Low** | 128k | Smallest | Podcasts, audiobooks |
| **Medium** | 192k | Small | General listening |
| **High** | 256k | Medium | Music, high quality |
| **Custom** | 320k | Largest | Studio quality, archiving |

### Sample Rates
- **Auto**: Keep original (recommended)
- **44.1 kHz**: CD quality
- **48 kHz**: Professional/studio

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + C` | Stop servers |
| `Esc` | Close dialogs |
| Click upload zone | Open file picker |

## 📊 Status Codes

### Job Status
- `queued` - Created, waiting
- `processing` - Converting
- `completed` - Done successfully
- `failed` - Error occurred
- `cancelled` - User cancelled

### File Status
- `pending` - Waiting
- `processing` - Converting
- `completed` - Done
- `failed` - Error

## 🔢 Ports

| Port | Service |
|------|---------|
| 3000 | Frontend (Next.js) |
| 8000 | Backend (FastAPI) |

## 📦 Dependencies

### Backend
```bash
fastapi uvicorn sqlalchemy pydantic
```

### Frontend
```bash
next react axios date-fns
```

### System
```bash
python3 (3.8+)
node (20.9.0+)
ffmpeg
```

## 🧪 Testing

### Test Backend
```bash
# Health check
curl http://localhost:8000/api/health

# Should return: {"status":"healthy",...}
```

### Test Frontend
```bash
# Open in browser
open http://localhost:3000

# Should see: Upload page
```

### Test Conversion
```bash
# Upload a test file via UI
# Start conversion
# Check logs: tail -f backend.log
# Verify output in storage/outputs/
```

## 🔄 Update & Reinstall

```bash
# Pull latest changes
git pull

# Reinstall dependencies
make install

# Clear cache
make clean

# Restart
./dev.sh
```

## 🆘 Common Error Messages

### "Port already in use"
```bash
make stop
# OR
kill -9 $(lsof -ti:8000)
```

### "Module not found"
```bash
pip install -r backend_requirements.txt
cd frontend && npm install
```

### "ffmpeg not found"
```bash
brew install ffmpeg
```

### "Database locked"
```bash
# Stop all processes
make stop
# Restart
./dev.sh
```

### "Cannot connect to backend"
- Check backend is running: http://localhost:8000/api/health
- Check NEXT_PUBLIC_API_URL in frontend/.env.local
- Check CORS settings in backend/main.py

## 📚 Documentation Links

- **[Setup Guide](SETUP.md)** - Installation
- **[User Guide](USER_GUIDE.md)** - How to use
- **[API Documentation](API.md)** - API reference
- **[Development Guide](DEVELOPMENT.md)** - For developers

## 💡 Tips

- **Parallel processing**: Upload multiple files at once for faster conversion
- **Quality vs Speed**: Lower bitrate = faster conversion
- **Storage**: Jobs auto-delete after 7 days
- **Performance**: Close other apps for faster conversion
- **Logs**: Always check logs first when troubleshooting
- **Database**: Backup data/jobs.db before resetting

---

**Need more details?** See the [full documentation](README.md).
