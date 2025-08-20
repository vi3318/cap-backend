#!/bin/bash

echo "🚂 Railway Build Optimization Script"
echo "=================================="

# Install only essential packages first
echo "📦 Installing core dependencies..."
pip install --no-cache-dir -r requirements-railway-minimal.txt

# Install Playwright separately (can be slow)
echo "🌐 Installing Playwright..."
pip install playwright==1.40.0

# Install browser binaries in background
echo "🔧 Installing browser binaries..."
playwright install chromium &

# Install remaining packages
echo "📚 Installing additional packages..."
pip install --no-cache-dir -r requirements-railway.txt

# Wait for Playwright installation
wait

echo "✅ Build optimization complete!"
echo "🚀 Ready for Railway deployment!" 