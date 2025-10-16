# 🚀 Cloud Deployment Guide - Railway

## Quick Deployment Steps

### 1. Push to GitHub
```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit - NZ Property Flip Calculator"

# Create repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/nz-property-flip-calculator.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Railway

#### Option A: Railway CLI (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy
railway link
railway up
```

#### Option B: Railway Web Interface
1. Go to https://railway.app
2. Sign up/Login with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository
6. Railway will auto-detect and deploy

### 3. Environment Variables
Set these in Railway dashboard:
```
DATABASE_URL=postgresql://postgres:password@host:port/database
PORT=5000
```

### 4. Frontend Deployment (Separate Service)
The backend will be deployed first. For the frontend:
1. Create a new Railway project
2. Connect the same GitHub repo
3. Set build command: `cd frontend && npm run build`
4. Set start command: `cd frontend && npm run preview`

## Expected URLs
- Backend API: `https://your-app-name.up.railway.app`
- Frontend: `https://your-frontend-name.up.railway.app`

## Testing
1. Backend health check: `https://your-app-name.up.railway.app/health`
2. Frontend: `https://your-frontend-name.up.railway.app`

## Free Tier Limits
- 500 hours/month
- 1GB RAM
- $5 credit monthly
- Perfect for testing and small projects
