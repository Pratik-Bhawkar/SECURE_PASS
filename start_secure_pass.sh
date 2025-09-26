#!/bin/bash

echo "========================================"
echo "    SECURE PASS - Starting Services"
echo "========================================"
echo

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed or not in PATH"
    echo "Please install Node.js 16+ and try again"
    exit 1
fi

echo "✓ Python and Node.js are installed"
echo

# Function to start backend
start_backend() {
    echo "Starting Backend API Server..."
    cd "$SCRIPT_DIR/SECURE_PASS_BACKEND"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv 2>/dev/null || python -m venv .venv
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Start the server
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}

# Function to start frontend
start_frontend() {
    echo "Starting Frontend Development Server..."
    cd "$SCRIPT_DIR/SECURE_PASS_FRONTEND"
    
    # Install dependencies
    npm install
    
    # Start the development server
    npm run dev
}

# Start backend in background
start_backend &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
start_frontend &
FRONTEND_PID=$!

echo
echo "========================================"
echo "Services are running..."
echo "Backend API: http://localhost:8000"
echo "Frontend UI: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
echo "========================================"
echo
echo "Press Ctrl+C to stop both services"

# Wait for user interrupt
trap 'echo "Stopping services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT
wait