# 🚂 Railway Backend Deployment Guide

## 🎯 **Complete Steps to Deploy on Railway**

### **Prerequisites:**
- GitHub account
- Railway account (free tier available)
- Your backend code ready

---

## **Step 1: Install Railway CLI**
```bash
npm install -g @railway/cli
```

---

## **Step 2: Login to Railway**
```bash
railway login
```
- Opens browser for authentication
- Authorize Railway to access your GitHub

---

## **Step 3: Navigate to Backend Directory**
```bash
cd backend
```

---

## **Step 4: Initialize Railway Project**
```bash
railway init
```
- Choose "Create new project"
- Give it a name: `researchdoc-ai-backend`
- Choose your GitHub account

---

## **Step 5: Configure Environment Variables**
```bash
railway variables set DATABASE_URL="postgresql://..."
railway variables set OPENAI_API_KEY="your-key-here"
railway variables set HUGGINGFACE_TOKEN="your-token-here"
```

**Required Variables:**
- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Railway sets this automatically
- `NODE_ENV` - Set to "production"

---

## **Step 6: Deploy to Railway**
```bash
railway up
```

---

## **Step 7: Get Your Live URL**
```bash
railway status
```
- Copy the generated URL
- Format: `https://your-app-name.railway.app`

---

## **Step 8: Update Frontend**
Update your frontend API calls to use the Railway URL:
```javascript
// Change from:
const API_BASE = 'http://localhost:8000';

// To:
const API_BASE = 'https://your-app-name.railway.app';
```

---

## **🚨 Important Notes:**

### **Database Setup:**
- Railway provides PostgreSQL
- Update `DATABASE_URL` in Railway variables
- Run migrations: `railway run alembic upgrade head`

### **File Storage:**
- Railway has ephemeral storage
- Consider using AWS S3 or similar for file uploads

### **Environment Variables:**
- Set all sensitive data in Railway dashboard
- Never commit `.env` files

### **Monitoring:**
- Check Railway dashboard for logs
- Monitor resource usage
- Set up alerts for errors

---

## **🔧 Troubleshooting:**

### **Build Failures:**
```bash
railway logs
railway run python -c "import app.main"
```

### **Runtime Errors:**
```bash
railway logs --tail
```

### **Database Issues:**
```bash
railway run alembic current
railway run alembic upgrade head
```

---

## **🎉 Success Indicators:**
- ✅ Build completes without errors
- ✅ App starts successfully
- ✅ Health endpoint responds: `/health`
- ✅ Paper search works: `/search-papers`
- ✅ Frontend can connect to backend

---

## **📱 Next Steps After Deployment:**
1. Test all API endpoints
2. Update frontend API base URL
3. Test paper search functionality
4. Monitor performance and logs
5. Set up custom domain (optional)

---

## **💡 Pro Tips:**
- Use Railway's free tier for development
- Upgrade to paid plan for production
- Set up automatic deployments from GitHub
- Monitor resource usage to avoid overages
- Use Railway's built-in PostgreSQL for simplicity 