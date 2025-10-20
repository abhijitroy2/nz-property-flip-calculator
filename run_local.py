#!/usr/bin/env python3
"""
Local development server runner
This creates a standalone FastAPI server for local testing without affecting production
"""
import sys
import os
import asyncio
from pathlib import Path

# Add the app directory to Python path for local development
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

# Create a local app instance that bypasses the import issues
from fastapi import FastAPI, UploadFile, File, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import csv, io
from datetime import datetime, date, timedelta
import os
import re
import time
import asyncio
from typing import List, Dict, Any
import logging

# Create FastAPI app
app = FastAPI(title="NZ Property Flip Calculator - Local Dev", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def index(request: Request):
    return HTMLResponse(content="""
    <h1>NZ Property Flip Calculator - Local Development</h1>
    <p>🚀 Local development server is running!</p>
    <p>📍 <a href="/docs">API Documentation</a></p>
    <p>📍 <a href="/health">Health Check</a></p>
    <p>📍 <a href="http://localhost:3000">React Frontend (run separately)</a></p>
    """)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "environment": "local"}

@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload and process CSV file with property data"""
    try:
        logging.info(f"Upload attempt: filename={file.filename}, content_type={file.content_type}")
        
        if not file.filename:
            logging.error("No filename provided")
            raise HTTPException(status_code=400, detail="No file provided")
        
        if not file.filename.lower().endswith((".csv", ".txt")):
            logging.error(f"Invalid file type: {file.filename}")
            raise HTTPException(status_code=400, detail="Only CSV or TXT files supported")

        content = await file.read()
        logging.info(f"File size: {len(content)} bytes")
        
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        try:
            buf = io.StringIO(content.decode("utf-8", errors="ignore"))
            reader = csv.reader(buf)
            rows = list(reader)
        except Exception as e:
            logging.error(f"CSV parsing error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

        if not rows:
            logging.warning("No data found in file")
            return {"properties": [], "message": "No data found in file"}

        headers = [h.strip() for h in rows[0]]
        logging.info(f"CSV headers: {headers}")
        
        properties = []
        
        for i, row in enumerate(rows[1:], 1):
            if len(row) < len(headers):
                row.extend([''] * (len(headers) - len(row)))
            
            property_data = dict(zip(headers, row))
            properties.append(property_data)
        
        logging.info(f"Successfully processed {len(properties)} properties")
        return {"properties": properties, "total": len(properties)}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Unexpected error in upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting LOCAL development server...")
    print("📍 Backend: http://localhost:5001")
    print("📍 Frontend: http://localhost:3000 (run separately)")
    print("📍 API Docs: http://localhost:5001/docs")
    print("📍 Health: http://localhost:5001/health")
    print("\n💡 To test upload:")
    print("   python test_upload_local.py")
    print("\nPress Ctrl+C to stop")
    
    uvicorn.run(
        app,  # Use the app instance directly
        host="127.0.0.1",
        port=5001,  # Use different port to avoid conflicts
        reload=False  # Disable reload when passing app instance
    )
