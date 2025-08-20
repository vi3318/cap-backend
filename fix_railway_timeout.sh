#!/bin/bash

echo "🚨 RAILWAY BUILD TIMEOUT FIX"
echo "============================"

echo "1. 🗑️  Removing heavy dependencies..."
# Remove problematic packages that cause timeouts
pip uninstall -y playwright selenium beautifulsoup4

echo "2. 📦 Installing minimal requirements..."
pip install --no-cache-dir -r requirements-railway-minimal.txt

echo "3. 🔧 Installing essential packages only..."
pip install --no-cache-dir playwright==1.40.0

echo "4. 🌐 Installing only Chromium (faster)..."
playwright install chromium

echo "5. ✅ Creating optimized build..."
echo "   - Use requirements-railway-minimal.txt"
echo "   - Use Dockerfile instead of NIXPACKS"
echo "   - Remove heavy ML packages temporarily"

echo ""
echo "🚀 NEXT STEPS:"
echo "1. Use Dockerfile: railway up --dockerfile"
echo "2. Or use minimal requirements: railway up"
echo "3. Add heavy packages back after successful deployment" 