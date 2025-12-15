.PHONY: help dev backend frontend install clean stop

help:
	@echo "MP3 Extractor - Available Commands:"
	@echo ""
	@echo "  make dev        - Start both backend and frontend servers"
	@echo "  make backend    - Start only the backend server"
	@echo "  make frontend   - Start only the frontend server"
	@echo "  make install    - Install all dependencies"
	@echo "  make clean      - Clean logs and cache files"
	@echo "  make stop       - Stop all running servers"
	@echo ""

dev:
	@echo "🚀 Starting both servers..."
	@./dev.sh

backend:
	@echo "📦 Starting backend on http://localhost:8000..."
	@python3 -m uvicorn backend.main:app --reload --port 8000

frontend:
	@echo "⚛️  Starting frontend on http://localhost:3000..."
	@cd frontend && npm run dev

install:
	@echo "📦 Installing backend dependencies..."
	@pip install -r backend_requirements.txt
	@echo "📦 Installing frontend dependencies..."
	@cd frontend && npm install
	@echo "✅ All dependencies installed!"

clean:
	@echo "🧹 Cleaning logs and cache..."
	@rm -f backend.log frontend.log
	@rm -rf frontend/.next
	@rm -rf frontend/node_modules/.cache
	@echo "✅ Cleaned!"

stop:
	@echo "🛑 Stopping servers..."
	@-pkill -f "uvicorn backend.main:app"
	@-pkill -f "next dev"
	@echo "✅ Servers stopped!"
