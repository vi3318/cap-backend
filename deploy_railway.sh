#!/bin/bash

echo "🚂 Deploying ResearchDoc AI Backend to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway (if not already logged in)
echo "🔐 Logging into Railway..."
railway login

# Initialize Railway project (if not already done)
if [ ! -f ".railway" ]; then
    echo "🚀 Initializing Railway project..."
    railway init
fi

# Deploy to Railway
echo "📦 Deploying to Railway..."
railway up

echo "✅ Deployment complete!"
echo "🌐 Your backend is now live on Railway!"
echo "📋 Check Railway dashboard for the URL" 