# Deployment Guide

## Docker Deployment (Recommended for Testing)

### Prerequisites
- Docker Desktop installed
- Docker Compose installed

### Quick Start with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove all data
docker-compose down -v
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- PostgreSQL: localhost:5432

### Docker Commands

```bash
# Rebuild containers
docker-compose build

# Restart a specific service
docker-compose restart backend

# View service status
docker-compose ps

# Execute commands in container
docker-compose exec backend python -c "print('Hello')"
docker-compose exec postgres psql -U postgres -d nz_property_flip
```

## Production Deployment

### Option 1: Cloud VM (Azure/AWS/GCP)

1. **Provision VM**:
   - OS: Ubuntu 20.04 LTS
   - RAM: 4GB minimum
   - Storage: 20GB minimum

2. **Install Dependencies**:
   ```bash
   sudo apt update
   sudo apt install -y python3.11 python3-pip nodejs npm postgresql
   ```

3. **Setup Application**:
   ```bash
   git clone <repository>
   cd realflip2
   ./setup.sh
   ```

4. **Configure Nginx** (optional):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:3000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location /api {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **Setup Systemd Services**:

   Backend service (`/etc/systemd/system/nz-property-backend.service`):
   ```ini
   [Unit]
   Description=NZ Property Flip Calculator Backend
   After=network.target postgresql.service

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/opt/realflip2/backend
   Environment="PATH=/opt/realflip2/backend/venv/bin"
   ExecStart=/opt/realflip2/backend/venv/bin/python app.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Frontend service (`/etc/systemd/system/nz-property-frontend.service`):
   ```ini
   [Unit]
   Description=NZ Property Flip Calculator Frontend
   After=network.target

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/opt/realflip2/frontend
   ExecStart=/usr/bin/npm run dev
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   sudo systemctl enable nz-property-backend nz-property-frontend
   sudo systemctl start nz-property-backend nz-property-frontend
   ```

### Option 2: Heroku Deployment

1. **Backend (Heroku)**:
   ```bash
   cd backend
   echo "web: gunicorn app:app" > Procfile
   pip install gunicorn
   pip freeze > requirements.txt
   
   heroku create nz-property-flip-backend
   heroku addons:create heroku-postgresql:hobby-dev
   git push heroku main
   ```

2. **Frontend (Vercel/Netlify)**:
   ```bash
   cd frontend
   npm run build
   # Deploy dist/ folder to Vercel or Netlify
   ```

### Option 3: Docker on Cloud

Deploy docker-compose.yml to:
- Azure Container Instances
- AWS ECS
- Google Cloud Run
- DigitalOcean App Platform

## Environment Variables for Production

Backend `.env`:
```env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=https://your-frontend-domain.com

# Scraping (more conservative in production)
CACHE_EXPIRY_DAYS=14
RATE_LIMIT_MIN_DELAY=5
RATE_LIMIT_MAX_DELAY=10
```

## Security Considerations

1. **Database**:
   - Use strong passwords
   - Restrict access to localhost or private network
   - Enable SSL connections

2. **API**:
   - Add authentication/API keys
   - Implement rate limiting
   - Enable HTTPS

3. **Scraping**:
   - Respect robots.txt
   - Use longer delays in production
   - Monitor for IP blocks

## Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:5000/health

# Database connection
curl http://localhost:5000/api/search
```

### Logs

```bash
# Docker
docker-compose logs -f backend
docker-compose logs -f frontend

# Systemd
sudo journalctl -u nz-property-backend -f
sudo journalctl -u nz-property-frontend -f
```

## Backup and Restore

### Database Backup

```bash
# Backup
pg_dump -U postgres nz_property_flip > backup_$(date +%Y%m%d).sql

# Restore
psql -U postgres nz_property_flip < backup_20231201.sql
```

### Automated Backups

Add to crontab:
```bash
0 2 * * * pg_dump -U postgres nz_property_flip > /backups/nz_property_$(date +\%Y\%m\%d).sql
```

## Scaling Considerations

1. **Database**: 
   - Use connection pooling
   - Add read replicas for analytics
   - Consider managed PostgreSQL (RDS, Cloud SQL)

2. **Backend**:
   - Use gunicorn with multiple workers
   - Deploy behind load balancer
   - Add Redis for caching

3. **Scraping**:
   - Use task queue (Celery + Redis)
   - Distribute scraping across workers
   - Implement proxy rotation if needed

## Troubleshooting

### High Memory Usage
- Reduce scraping concurrency
- Increase cache expiry time
- Add swap space

### Slow Performance
- Enable PostgreSQL query caching
- Add indexes to database
- Use CDN for frontend

### Scraping Blocks
- Increase rate limiting delays
- Use residential proxies
- Implement rotating user agents

