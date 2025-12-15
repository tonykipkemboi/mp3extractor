# MP3 Extractor

Convert MP4 videos to high-quality MP3 audio files with both a powerful CLI tool and a modern web interface.

## 🎯 Choose Your Interface

### 🖥️ Web Application (Recommended)

Modern, user-friendly web interface with drag-and-drop, real-time progress, and batch processing.

**Quick Start:**
```bash
./dev.sh
# Open http://localhost:3000
```

👉 **[Web UI Documentation](docs/README.md)** - Setup, usage, and API reference

### ⌨️ Command Line Interface

Fast, scriptable CLI tool for developers and power users.

**Quick Start:**
```bash
python mp4-to-mp3-extractor.py input.mp4 output.mp3
```

👉 **[CLI Documentation](README.md)** - Commands and options

---

## 📚 Documentation

### For Users

- **[Setup Guide](docs/SETUP.md)** - Install and configure the application
- **[User Guide](docs/USER_GUIDE.md)** - How to use the web interface

### For Developers

- **[API Documentation](docs/API.md)** - REST API reference
- **[Development Guide](docs/DEVELOPMENT.md)** - Architecture and contributing

### For Both

- **[Web UI Overview](README_WEB.md)** - Technical details about the web application
- **[CLI Tool](README.md)** - Original CLI tool documentation

---

## ⚡ Quick Comparison

| Feature | Web UI | CLI |
|---------|--------|-----|
| **Ease of Use** | ⭐⭐⭐⭐⭐ Drag & drop | ⭐⭐⭐ Command line |
| **Real-time Progress** | ✅ Visual progress bars | ✅ Terminal progress |
| **Batch Processing** | ✅ Up to 3 parallel | ✅ Configurable |
| **Job History** | ✅ Web interface | ❌ |
| **Quality Presets** | ✅ GUI presets | ⚙️ Manual flags |
| **Automation** | ⚙️ API integration | ✅ Scripts |
| **Best For** | General users | Power users, automation |

---

## 🚀 Quick Start

### Web Application

1. **Install dependencies:**
```bash
make install
```

2. **Start servers:**
```bash
./dev.sh
```

3. **Open browser:**
```
http://localhost:3000
```

4. **Convert files:**
- Drag and drop MP4 files
- Configure quality settings
- Click "Start Conversion"
- Download MP3 files

### CLI Tool

1. **Install:**
```bash
pip install -r requirements.txt
```

2. **Convert:**
```bash
# Single file
python mp4-to-mp3-extractor.py video.mp4 audio.mp3

# Directory
python mp4-to-mp3-extractor.py --input-dir videos/ --output-dir audio/

# Custom quality
python mp4-to-mp3-extractor.py video.mp4 audio.mp3 --bitrate 320k
```

---

## 🎨 Features

### Web Application

✅ **Modern UI** - Beautiful interface built with Next.js and shadcn/ui
✅ **Drag & Drop** - Easy file upload
✅ **Real-time Progress** - Live conversion updates via SSE
✅ **Batch Processing** - Convert multiple files simultaneously
✅ **Quality Presets** - Low, Medium, High, Custom
✅ **Job History** - View and manage past conversions
✅ **Download Options** - Individual files or ZIP archive
✅ **Dark Mode** - Full dark mode support

### CLI Tool

✅ **High Quality** - LAME encoder with 320k bitrate default
✅ **Parallel Processing** - Multi-core support
✅ **Metadata Preservation** - Copy ID3 tags and artwork
✅ **Config Files** - YAML/JSON configuration
✅ **Progress Bars** - Real-time progress tracking
✅ **Cross-platform** - macOS, Linux, Windows

---

## 📦 What's Included

```
mp3extractor/
├── backend/              # FastAPI backend for web UI
├── frontend/             # Next.js web interface
├── mp3extractor/         # Python CLI package
├── docs/                 # Complete documentation
│   ├── README.md        # Documentation index
│   ├── SETUP.md         # Installation guide
│   ├── USER_GUIDE.md    # Web UI usage
│   ├── API.md           # API reference
│   └── DEVELOPMENT.md   # Developer guide
├── dev.sh               # Start web application
├── Makefile             # Convenient commands
├── .aliases             # Shell aliases
├── README.md            # CLI documentation
├── README_WEB.md        # Web UI technical details
└── README_MAIN.md       # This file
```

---

## 🛠️ Tech Stack

### Web Application

- **Frontend**: Next.js 14, shadcn/ui, TypeScript, Tailwind CSS
- **Backend**: FastAPI, SQLAlchemy, SQLite
- **Real-time**: Server-Sent Events (SSE)
- **Audio**: ffmpeg via mp3extractor package

### CLI Tool

- **Language**: Python 3.8+
- **Audio**: ffmpeg with libmp3lame
- **Progress**: tqdm
- **Metadata**: mutagen

---

## 🎓 Getting Started Paths

### I want to use it (non-technical)

1. Read **[Setup Guide](docs/SETUP.md)**
2. Read **[User Guide](docs/USER_GUIDE.md)**
3. Use the Web UI at http://localhost:3000

### I want to automate conversions

1. Read **[CLI Documentation](README.md)**
2. Write scripts using the CLI tool
3. Or use the **[API](docs/API.md)** with the web backend

### I want to integrate into my app

1. Read **[API Documentation](docs/API.md)**
2. Start backend: `make backend`
3. Make HTTP requests to http://localhost:8000

### I want to contribute

1. Read **[Development Guide](docs/DEVELOPMENT.md)**
2. Set up development environment
3. Pick an issue or feature to work on

---

## 📊 Architecture

### Web Application Architecture

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
                          │ Database │         │ (uploads/  │   │ (via CLI │
                          │          │         │  outputs)  │   │ package) │
                          └──────────┘         └────────────┘   └─────────┘
```

---

## 🔧 Common Commands

### Web Application

```bash
# Start everything
./dev.sh
make dev
mp3dev              # (after alias setup)

# Stop services
make stop
mp3stop

# View logs
tail -f backend.log
tail -f frontend.log
mp3logs

# Clean up
make clean
mp3clean
```

### CLI Tool

```bash
# Convert single file
python mp4-to-mp3-extractor.py video.mp4 audio.mp3

# Batch convert
python mp4-to-mp3-extractor.py --input-dir videos/ --output-dir audio/

# Custom settings
python mp4-to-mp3-extractor.py video.mp4 audio.mp3 \
  --bitrate 320k \
  --sample-rate 48000 \
  --preserve-metadata
```

---

## 🐛 Troubleshooting

### Quick Fixes

**Backend won't start:**
```bash
pip install -r backend_requirements.txt
python3 -m uvicorn backend.main:app --reload --port 8000
```

**Frontend won't start:**
```bash
cd frontend && npm install && npm run dev
```

**ffmpeg not found:**
```bash
# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

**Port already in use:**
```bash
make stop
# Or: kill -9 $(lsof -ti:8000)
```

👉 **More help:** See [Setup Guide - Troubleshooting](docs/SETUP.md#troubleshooting)

---

## 📖 Examples

### Web UI Example

1. Open http://localhost:3000
2. Drag `video.mp4` into upload zone
3. Select "High (256k)" quality preset
4. Click "Start Conversion"
5. Click "Download" when complete

### CLI Example

```bash
# Convert with highest quality
python mp4-to-mp3-extractor.py \
  --input videos/lecture.mp4 \
  --output audio/lecture.mp3 \
  --bitrate 320k \
  --preserve-metadata

# Batch convert all videos in a folder
python mp4-to-mp3-extractor.py \
  --input-dir ~/Downloads/videos/ \
  --output-dir ~/Music/ \
  --parallel 4
```

### API Example

```bash
# Upload file
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/files/upload \
  -F "files=@video.mp4")

JOB_ID=$(echo $RESPONSE | jq -r '.job_id')

# Start conversion
curl -X POST http://localhost:8000/api/v1/convert/start \
  -H "Content-Type: application/json" \
  -d "{\"job_id\":\"$JOB_ID\",\"config\":{\"bitrate\":\"320k\"}}"

# Download result
curl -O "http://localhost:8000/api/v1/files/download/$JOB_ID/video.mp3"
```

---

## 🤝 Contributing

We welcome contributions! See the [Development Guide](docs/DEVELOPMENT.md) for:

- Architecture overview
- Setup instructions
- Coding guidelines
- Pull request process

Areas for contribution:
- Additional audio formats (WAV, AAC, OGG)
- User authentication
- Docker support
- Mobile app
- Tests

---

## 📄 License

[Your license here]

---

## 🙏 Acknowledgments

Built with:
- [ffmpeg](https://ffmpeg.org/) - Audio/video processing
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [Next.js](https://nextjs.org/) - Frontend framework
- [shadcn/ui](https://ui.shadcn.com/) - UI components

---

## 🆘 Support

1. **Check documentation**: Start with [docs/README.md](docs/README.md)
2. **API issues**: Check http://localhost:8000/docs
3. **View logs**: `tail -f backend.log frontend.log`
4. **Common issues**: See [Setup Guide](docs/SETUP.md#troubleshooting)

---

## 🎯 What's Next?

### For Users
→ Start with **[Setup Guide](docs/SETUP.md)**

### For Developers
→ Start with **[Development Guide](docs/DEVELOPMENT.md)**

### For API Integration
→ Start with **[API Documentation](docs/API.md)**

---

**Ready to convert? [Get Started →](docs/SETUP.md)**
