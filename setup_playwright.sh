#!/bin/bash

echo "🚀 Setting up Playwright for web scraping..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Please run setup_backend.sh first."
    exit 1
fi

# Install Playwright
echo "📥 Installing Playwright..."
pip install playwright==1.40.0

# Install browser binaries
echo "🌐 Installing browser binaries..."
playwright install

# Install specific browsers
echo "🔧 Installing Chromium browser..."
playwright install chromium

echo "✅ Playwright setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Start your backend server: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo "2. Test the paper search functionality in your frontend"
echo ""
echo "🔍 Available paper search sources:"
echo "   - Google Scholar"
echo "   - arXiv"
echo "   - Semantic Scholar"
echo ""
echo "⚠️  Note: Web scraping may be subject to rate limiting and terms of service."
echo "   Use responsibly and respect robots.txt files." 