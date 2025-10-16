# Railway Deployment Guide

## Deploying the NZ Property Flip Calculator

This guide will help you deploy both the frontend and backend to Railway in a single service.

### Prerequisites

1. Railway account (free tier available)
2. GitHub repository with your code
3. Railway CLI (optional but recommended)

### Deployment Steps

#### Option 1: Deploy via Railway Dashboard (Recommended)

1. **Connect GitHub Repository**
   - Go to [Railway.app](https://railway.app)
   - Sign in with your GitHub account
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `realflip2` repository

2. **Configure Build Settings**
   - Railway will auto-detect the `railway.json` configuration
   - The build will use `Dockerfile.frontend` which includes both frontend and backend

3. **Environment Variables** (Optional)
   - Go to your project settings → Variables
   - Add any environment variables you need:
     ```
     VITE_API_URL=https://your-backend-url.railway.app
     ```

4. **Deploy**
   - Railway will automatically build and deploy
   - The deployment includes:
     - React frontend (served by Nginx)
     - FastAPI backend (running on port 5000)
     - Nginx proxy (port 8080) routing requests

#### Option 2: Deploy via Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

### Architecture

The deployed application uses:

- **Nginx** (port 8080): Serves React frontend and proxies API calls
- **FastAPI** (port 5000): Backend API server
- **React Frontend**: Built and served as static files

### URL Structure

- `https://your-app.railway.app/` - React frontend
- `https://your-app.railway.app/api/` - Backend API
- `https://your-app.railway.app/health` - Health check

### Testing the Deployment

1. Visit your Railway URL
2. Upload a CSV file with property data
3. Click "Analyze Properties"
4. Review the flip potential analysis

### Troubleshooting

#### Build Issues
- Check Railway build logs for errors
- Ensure all dependencies are in `requirements.txt`
- Verify Dockerfile syntax

#### Runtime Issues
- Check Railway deployment logs
- Verify environment variables
- Test health endpoint: `/health`

#### Frontend Not Loading
- Check if static files are being served correctly
- Verify Nginx configuration
- Check browser console for errors

### Custom Domain (Optional)

1. Go to Railway project settings
2. Click "Domains"
3. Add your custom domain
4. Configure DNS records as instructed

### Monitoring

Railway provides:
- Real-time logs
- Performance metrics
- Automatic deployments on git push
- Health checks

### Cost

- Railway free tier: $5 credit monthly
- Paid plans start at $5/month
- No credit card required for free tier

### Next Steps

After deployment:
1. Test all functionality
2. Set up monitoring
3. Configure custom domain (optional)
4. Set up automated deployments
