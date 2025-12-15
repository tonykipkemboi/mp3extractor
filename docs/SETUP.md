# Setup Guide

Complete installation and setup instructions for the MP3 Extractor Web UI.

## Prerequisites

### Required Software

- **Python 3.8+** (3.12 recommended)
- **Node.js 20.9.0+** (25.2.1 recommended)
- **ffmpeg** (for audio conversion)
- **pip** (Python package manager)
- **npm** (Node package manager)

### Install Prerequisites

**macOS:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required software
brew install python node ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip nodejs npm ffmpeg
```

**Windows:**
- Install Python from [python.org](https://www.python.org/downloads/)
- Install Node.js from [nodejs.org](https://nodejs.org/)
- Install ffmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)

## Installation

### 1. Clone/Download the Repository

```bash
cd /path/to/your/projects
# If you have the project, navigate to it
cd mp3extractor
```

### 2. Install Dependencies

**Option 1: Using Make (Recommended)**
```bash
make install
```

**Option 2: Manual Installation**

Backend dependencies:
```bash
pip install -r backend_requirements.txt
```

Frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

### 3. Create Required Directories

```bash
mkdir -p storage/uploads storage/outputs data
```

### 4. Environment Configuration (Optional)

Create `.env` file in the project root (optional, has defaults):

```env
# Backend Configuration
DATABASE_URL=sqlite:///./data/jobs.db
STORAGE_PATH=./storage
MAX_UPLOAD_SIZE=524288000  # 500MB
FILE_RETENTION_DAYS=7
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 5. Verify Installation

Check that all dependencies are installed:

```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check Node version
node --version     # Should be 20.9.0+

# Check ffmpeg
ffmpeg -version

# Check pip packages
pip list | grep fastapi
pip list | grep sqlalchemy

# Check npm packages
cd frontend && npm list --depth=0 | grep next
```

## First Run

### Start the Application

**Option 1: Quick Start (Both Servers)**
```bash
./dev.sh
```

**Option 2: Make Command**
```bash
make dev
```

**Option 3: Separate Terminals**

Terminal 1 - Backend:
```bash
python3 -m uvicorn backend.main:app --reload --port 8000
```

Terminal 2 - Frontend:
```bash
cd frontend && npm run dev
```

### Verify Services Are Running

1. Backend health check:
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected"
}
```

2. Open in browser:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Optional: Shell Aliases

For quick access from any directory:

```bash
# Add to ~/.zshrc or ~/.bashrc
source /Users/tonykipkemboi/mp3extractor/.aliases

# Reload shell
source ~/.zshrc
```

Now you can use:
```bash
mp3dev      # Start the app
mp3stop     # Stop all servers
mp3logs     # View logs
mp3clean    # Clean up
```

## Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
lsof -ti:8000
lsof -ti:3000

# Kill the process
kill -9 $(lsof -ti:8000)
kill -9 $(lsof -ti:3000)

# Or use the stop command
make stop
```

### Backend Won't Start

1. Check Python version: `python3 --version`
2. Reinstall dependencies: `pip install -r backend_requirements.txt`
3. Check database directory exists: `mkdir -p data`
4. Check logs: `tail -f backend.log`

### Frontend Won't Start

1. Check Node version: `node --version`
2. Clear cache and reinstall:
```bash
cd frontend
rm -rf node_modules .next
npm install
```
3. Check logs: `tail -f frontend.log`

### ffmpeg Not Found

The conversion will fail if ffmpeg is not installed:

```bash
# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg

# Verify
ffmpeg -version
```

### Permission Errors

```bash
# Fix storage permissions
chmod -R 755 storage data

# Make scripts executable
chmod +x dev.sh
```

### Database Issues

```bash
# Reset database (WARNING: deletes all data)
rm data/jobs.db

# Restart backend to recreate
python3 -m uvicorn backend.main:app --reload --port 8000
```

## Next Steps

- Read the [User Guide](USER_GUIDE.md) to learn how to use the application
- Read the [API Documentation](API.md) for API details
- Read the [Development Guide](DEVELOPMENT.md) for contributing

## Uninstall

To completely remove the application:

```bash
# Remove Python packages
pip uninstall -y -r backend_requirements.txt

# Remove Node packages
cd frontend && rm -rf node_modules

# Remove data and storage
rm -rf data storage backend.log frontend.log

# Remove aliases from ~/.zshrc
# Manually edit ~/.zshrc and remove the MP3 Extractor section
```
