#!/bin/bash

# Start FastAPI backend in background
python -m uvicorn app.main:app --host 0.0.0.0 --port 5000 &

# Start nginx in foreground
nginx -g "daemon off;"
