# 🐳 Docker Setup (Easiest Option)

## Prerequisites
Your friend only needs to install **Docker Desktop** from https://docker.com/

## One-Command Setup
```bash
# Clone or download the project
# Navigate to project folder
# Run this single command:
docker-compose up
```

That's it! The app will be available at http://localhost:3000

## What Docker Does
- Automatically sets up PostgreSQL database
- Installs all Python dependencies
- Installs all Node.js dependencies
- Runs both backend and frontend servers
- No manual configuration needed!

## Stopping the App
```bash
docker-compose down
```

## Benefits
- ✅ No need to install Python, Node.js, or PostgreSQL
- ✅ Consistent environment across different computers
- ✅ One command setup
- ✅ Easy to share and deploy
