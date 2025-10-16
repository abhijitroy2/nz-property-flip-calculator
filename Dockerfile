FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ .

# Expose port (Railway will provide PORT env var)
EXPOSE 5000

# Run the application with gunicorn
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT --workers 2 app:create_app"]
