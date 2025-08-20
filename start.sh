#!/bin/bash

# Railway startup script for ResearchDoc AI Backend
echo "🚀 Starting ResearchDoc AI Backend..."

# Set default port if not provided
export PORT=${PORT:-8000}

echo "📡 Starting uvicorn on port $PORT"

# Start the application
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT