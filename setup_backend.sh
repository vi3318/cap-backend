#!/bin/bash

echo "🚀 Setting up Research Document Analysis System Backend"
echo "========================================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ pip3 found: $(pip3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install basic dependencies first
echo "📥 Installing core dependencies..."
pip install fastapi uvicorn python-multipart

# Install database dependencies
echo "🗄️ Installing database dependencies..."
pip install sqlalchemy

# Install document processing
echo "📄 Installing document processing libraries..."
pip install PyPDF2 python-docx Pillow langdetect

# Install AI/ML libraries
echo "🤖 Installing AI/ML libraries..."
pip install numpy pandas scikit-learn

# Install web scraping
echo "🕷️ Installing web scraping libraries..."
pip install requests beautifulsoup4

# Install knowledge graph
echo "🕸️ Installing knowledge graph libraries..."
pip install networkx

# Install utilities
echo "🔧 Installing utility libraries..."
pip install python-dotenv pydantic pydantic-settings python-dateutil pytz

# Install development tools
echo "🛠️ Installing development tools..."
pip install pytest pytest-asyncio httpx

# Create uploads directory
echo "📁 Creating uploads directory..."
mkdir -p uploads

# Copy environment file
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created. Please edit it with your configuration."
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Backend setup completed successfully!"
echo ""
echo "To start the backend server:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start server: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "To install additional dependencies later:"
echo "pip install -r requirements.txt"
echo ""
echo "Note: Some packages like psycopg2 (PostgreSQL) may require additional system dependencies."
echo "For development, SQLite is used by default." 