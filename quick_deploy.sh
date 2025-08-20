#!/bin/bash

echo "🚂 Quick Railway Deployment for ResearchDoc AI Backend"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    echo "   cd backend && ./quick_deploy.sh"
    exit 1
fi

# Install Railway CLI if not present
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Initialize project if needed
if [ ! -f ".railway" ]; then
    echo "🚀 Initializing Railway project..."
    railway init
fi

# Deploy
echo "📦 Deploying to Railway..."
railway up

echo ""
echo "🎉 Deployment complete!"
echo "🌐 Check your Railway dashboard for the live URL"
echo "📋 Run 'railway status' to see your app URL"
echo ""
echo "🔧 Next steps:"
echo "   1. Copy the Railway URL"
echo "   2. Update frontend API calls"
echo "   3. Test the deployed backend"
echo "   4. Set up environment variables in Railway dashboard" 