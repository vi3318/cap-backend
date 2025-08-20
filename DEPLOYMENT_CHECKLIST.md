# ✅ Railway Deployment Checklist

## 🚀 **Before You Start:**
- [ ] Backend code is working locally
- [ ] All tests pass
- [ ] No sensitive data in code
- [ ] GitHub repository is up to date

---

## 📋 **Deployment Steps:**

### **Step 1: Install Railway CLI**
```bash
npm install -g @railway/cli
```

### **Step 2: Login to Railway**
```bash
railway login
```

### **Step 3: Navigate to Backend**
```bash
cd backend
```

### **Step 4: Initialize Project**
```bash
railway init
# Choose: Create new project
# Name: researchdoc-ai-backend
```

### **Step 5: Deploy**
```bash
railway up
```

### **Step 6: Get URL**
```bash
railway status
# Copy the generated URL
```

---

## 🔧 **Post-Deployment Setup:**

### **Environment Variables (Set in Railway Dashboard):**
- [ ] `DATABASE_URL` - PostgreSQL connection
- [ ] `OPENAI_API_KEY` - Your OpenAI key
- [ ] `HUGGINGFACE_TOKEN` - Your HuggingFace token
- [ ] `NODE_ENV` - Set to "production"

### **Database Setup:**
- [ ] Run migrations: `railway run alembic upgrade head`
- [ ] Verify database connection

### **Test Endpoints:**
- [ ] Health check: `/health`
- [ ] Paper search: `/search-papers`
- [ ] Document upload: `/upload-document`

---

## 🌐 **Update Frontend:**

### **Change API Base URL:**
```javascript
// From:
const API_BASE = 'http://localhost:8000';

// To:
const API_BASE = 'https://your-app-name.railway.app';
```

### **Test Frontend:**
- [ ] Paper search works
- [ ] Document upload works
- [ ] All features functional

---

## 🚨 **Common Issues & Solutions:**

### **Build Fails:**
- Check `requirements-railway.txt`
- Verify Python version in `runtime.txt`
- Check Railway logs

### **Runtime Errors:**
- Verify environment variables
- Check database connection
- Monitor Railway logs

### **CORS Issues:**
- Update CORS origins in backend
- Add Railway domain to allowed origins

---

## 🎯 **Success Criteria:**
- [ ] Backend deploys without errors
- [ ] Health endpoint responds
- [ ] Paper search returns results
- [ ] Frontend can connect
- [ ] All features work as expected

---

## 📱 **Next Steps:**
1. Set up automatic deployments
2. Configure custom domain
3. Set up monitoring
4. Scale resources as needed 