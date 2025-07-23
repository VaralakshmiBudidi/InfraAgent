# 🚀 Deploying InfraAgent to Render

This guide will walk you through deploying your InfraAgent application to Render, a cloud platform that offers free hosting for web applications.

## 📋 Prerequisites

1. **GitHub Account**: Your code should be in a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **GitHub Personal Access Token** (optional): For webhook functionality

## 🎯 Deployment Steps

### Step 1: Prepare Your Repository

1. **Push your code to GitHub** (if not already done):
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Verify these files exist in your repository**:
   - `render.yaml` (deployment configuration)
   - `backend/requirements.txt` (Python dependencies)
   - `frontend/package.json` (Node.js dependencies)

### Step 2: Deploy to Render

#### Option A: Using render.yaml (Recommended)

1. **Go to [render.com](https://render.com)** and sign in
2. **Click "New +"** and select **"Blueprint"**
3. **Connect your GitHub repository**
4. **Select the repository** containing your InfraAgent code
5. **Render will automatically detect** the `render.yaml` file
6. **Click "Apply"** to start the deployment

#### Option B: Manual Deployment

If you prefer to deploy services individually:

**Backend Service:**
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `infraagent-backend`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

**Frontend Service:**
1. Click "New +" → "Static Site"
2. Connect your GitHub repository
3. Configure:
   - **Name**: `infraagent-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/build`
   - **Plan**: Free

### Step 3: Configure Environment Variables

For the **Backend Service**, add these environment variables:

| Key | Value | Description |
|-----|-------|-------------|
| `ENVIRONMENT` | `production` | Set to production mode |
| `DEBUG` | `false` | Disable debug mode |
| `WEBHOOK_URL` | `https://your-backend-url.onrender.com/webhook/github` | Your backend webhook URL |
| `DEPLOYMENT_DIR` | `/tmp/deployments` | Deployment directory |

**Optional (for GitHub webhooks):**
| Key | Value | Description |
|-----|-------|-------------|
| `GITHUB_TOKEN` | `your_github_token` | GitHub personal access token |
| `WEBHOOK_SECRET` | `your_secret` | Webhook secret for security |

For the **Frontend Service**, add:
| Key | Value | Description |
|-----|-------|-------------|
| `REACT_APP_API_URL` | `https://your-backend-url.onrender.com` | Your backend API URL |

### Step 4: Wait for Deployment

1. **Backend deployment** typically takes 2-3 minutes
2. **Frontend deployment** typically takes 1-2 minutes
3. **Monitor the logs** for any build errors

### Step 5: Test Your Deployment

1. **Backend Health Check**: Visit `https://your-backend-url.onrender.com/health`
2. **Frontend**: Visit `https://your-frontend-url.onrender.com`
3. **Test the full flow**: Try creating a deployment through the UI

## 🔧 Troubleshooting

### Common Issues

**Backend Build Fails:**
- Check that `backend/requirements.txt` exists and has correct dependencies
- Verify Python version compatibility (3.11+ recommended)

**Frontend Build Fails:**
- Ensure `frontend/package.json` has correct dependencies
- Check that all React components are properly imported

**CORS Errors:**
- Verify the backend CORS configuration includes your frontend URL
- Check that environment variables are set correctly

**API Connection Issues:**
- Ensure `REACT_APP_API_URL` is set to your backend URL
- Verify the backend is running and accessible

### Debugging

1. **Check Render Logs**: Go to your service → "Logs" tab
2. **Test API Endpoints**: Use tools like Postman or curl
3. **Verify Environment Variables**: Check they're set correctly in Render dashboard

## 🌐 Custom Domains (Optional)

1. **Go to your service** in Render dashboard
2. **Click "Settings"** → "Custom Domains"
3. **Add your domain** and configure DNS
4. **Update CORS settings** in `backend/app/main.py`

## 🔒 Security Considerations

1. **Environment Variables**: Never commit sensitive data to your repository
2. **GitHub Token**: Use minimal permissions for your GitHub token
3. **Webhook Secret**: Use a strong, random secret for webhooks
4. **HTTPS**: Render automatically provides SSL certificates

## 📊 Monitoring

1. **Health Checks**: Your backend has a `/health` endpoint
2. **Logs**: Monitor application logs in Render dashboard
3. **Metrics**: Render provides basic metrics for your services

## 🎉 Success!

Once deployed, your InfraAgent application will be available at:
- **Frontend**: `https://your-frontend-url.onrender.com`
- **Backend API**: `https://your-backend-url.onrender.com`

Your application is now live and accessible from anywhere! 🚀

---

**Need Help?**
- [Render Documentation](https://render.com/docs)
- [Render Community](https://community.render.com)
- [GitHub Issues](https://github.com/your-repo/issues) 