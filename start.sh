#!/bin/bash

# Railway startup script for ResearchDoc AI Backend
echo "🚀 Starting ResearchDoc AI Backend..."

# Railway sets PORT automatically - use it directly
echo "📡 Railway PORT: $PORT"
echo "📡 Starting uvicorn on port ${PORT:-8000}"

# Start the application with proper Railway PORT handling
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}