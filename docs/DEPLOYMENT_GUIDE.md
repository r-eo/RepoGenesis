# Sleep Quest - Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Production Deployment](#production-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Database Management](#database-management)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Python 3.8+** (Backend)
- **Node.js 14+** and **npm** (Frontend)
- **Git** (Version control)

### Optional (for production)
- **Nginx** or **Apache** (Reverse proxy)
- **PM2** or **systemd** (Process management)
- **PostgreSQL** or **MySQL** (Production database, optional)

---

## Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/sleep-quest.git
cd sleep-quest
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd server
pip install -r requirements.txt
```

**requirements.txt:**
```
Flask==2.3.0
Flask-CORS==4.0.0
Werkzeug==2.3.0
```

#### Initialize Database
```bash
# Run migration to create tables
python ../migrate_sleep_engine.py
```

#### Start Backend Server
```bash
python app.py
```

**Expected Output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
```

### 3. Frontend Setup

#### Install Node Dependencies
```bash
cd ../client
npm install
```

**Key Dependencies:**
- React 18.2.0
- Axios 1.4.0

#### Start Frontend Development Server
```bash
npm start
```

**Expected Output:**
```
Compiled successfully!
Local: http://localhost:3000
```

### 4. Verify Installation

1. Open browser to `http://localhost:3000`
2. Create a test account
3. Try `/sleep` command
4. Check reliability badge appears

---

## Production Deployment

### Option 1: Traditional Server (VPS/Dedicated)

#### 1. Server Preparation

**Update System:**
```bash
sudo apt update && sudo apt upgrade -y
```

**Install Dependencies:**
```bash
# Python
sudo apt install python3 python3-pip python3-venv -y

# Node.js (via NodeSource)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Nginx
sudo apt install nginx -y
```

#### 2. Deploy Backend

**Create Application Directory:**
```bash
sudo mkdir -p /var/www/sleep-quest
sudo chown $USER:$USER /var/www/sleep-quest
cd /var/www/sleep-quest
```

**Clone and Setup:**
```bash
git clone https://github.com/yourusername/sleep-quest.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd server
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server
```

**Create Production Config:**
```python
# server/config_prod.py
import os

class ProductionConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DATABASE = '/var/www/sleep-quest/server/database.db'
    DEBUG = False
```

**Create WSGI Entry Point:**
```python
# server/wsgi.py
from app import app

if __name__ == "__main__":
    app.run()
```

**Run Database Migration:**
```bash
python ../migrate_sleep_engine.py
```

**Test Gunicorn:**
```bash
gunicorn --bind 0.0.0.0:5000 wsgi:app
```

#### 3. Deploy Frontend

**Build Production Bundle:**
```bash
cd /var/www/sleep-quest/client
npm install
npm run build
```

**Output:** Creates `build/` directory with optimized static files.

#### 4. Configure Nginx

**Create Nginx Config:**
```bash
sudo nano /etc/nginx/sites-available/sleep-quest
```

**Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    # Frontend (React build)
    location / {
        root /var/www/sleep-quest/client/build;
        try_files $uri /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable Site:**
```bash
sudo ln -s /etc/nginx/sites-available/sleep-quest /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

#### 5. Setup Process Manager (systemd)

**Create Service File:**
```bash
sudo nano /etc/systemd/system/sleep-quest.service
```

**Service Configuration:**
```ini
[Unit]
Description=Sleep Quest Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/sleep-quest/server
Environment="PATH=/var/www/sleep-quest/venv/bin"
ExecStart=/var/www/sleep-quest/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 wsgi:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Start Service:**
```bash
sudo systemctl daemon-reload
sudo systemctl start sleep-quest
sudo systemctl enable sleep-quest  # Auto-start on boot
sudo systemctl status sleep-quest  # Check status
```

#### 6. SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

**Auto-renewal:**
```bash
sudo certbot renew --dry-run
```

---

### Option 2: Docker Deployment

#### 1. Create Dockerfile (Backend)

**server/Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "wsgi:app"]
```

#### 2. Create Dockerfile (Frontend)

**client/Dockerfile:**
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
```

**client/nginx.conf:**
```nginx
server {
    listen 80;
    location / {
        root /usr/share/nginx/html;
        try_files $uri /index.html;
    }
    location /api {
        proxy_pass http://backend:5000;
    }
}
```

#### 3. Docker Compose

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: ./server
    ports:
      - "5000:5000"
    volumes:
      - ./server/database.db:/app/database.db
    environment:
      - SECRET_KEY=${SECRET_KEY}
    restart: unless-stopped

  frontend:
    build: ./client
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

**Deploy:**
```bash
docker-compose up -d
```

---

### Option 3: Cloud Platforms

#### Heroku

**Backend (server/):**
```bash
# Create Procfile
echo "web: gunicorn wsgi:app" > Procfile

# Deploy
heroku create sleep-quest-api
git subtree push --prefix server heroku master
```

**Frontend (client/):**
```bash
# Deploy to Netlify/Vercel
npm run build
# Upload build/ folder to Netlify
```

#### AWS (EC2)
Follow "Traditional Server" steps on an EC2 instance.

#### DigitalOcean App Platform
1. Connect GitHub repository
2. Configure build commands:
   - Backend: `pip install -r requirements.txt`
   - Frontend: `npm install && npm run build`
3. Set environment variables
4. Deploy

---

## Environment Configuration

### Backend Environment Variables

**Create `.env` file:**
```bash
# server/.env
SECRET_KEY=your-super-secret-key-change-this
DATABASE_PATH=/path/to/database.db
DEBUG=False
FLASK_ENV=production
```

**Load in config.py:**
```python
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DATABASE = os.getenv('DATABASE_PATH', 'database.db')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
```

### Frontend Environment Variables

**Create `.env.production`:**
```bash
# client/.env.production
REACT_APP_API_URL=https://api.your-domain.com/api
```

**Update sleepApi.js:**
```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
```

---

## Database Management

### Backup

**SQLite Backup:**
```bash
# Manual backup
cp server/database.db server/database_backup_$(date +%Y%m%d).db

# Automated daily backup (cron)
0 2 * * * cp /var/www/sleep-quest/server/database.db /backups/database_$(date +\%Y\%m\%d).db
```

### Migration

**Run Migration:**
```bash
python migrate_sleep_engine.py
```

**Rollback (if needed):**
```bash
# Restore from backup
cp server/database_backup_20251122.db server/database.db
```

### Database Upgrade (SQLite → PostgreSQL)

**Install psycopg2:**
```bash
pip install psycopg2-binary
```

**Update config.py:**
```python
import psycopg2

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/sleepquest')
```

**Migrate Data:**
```bash
# Export SQLite
sqlite3 database.db .dump > dump.sql

# Import to PostgreSQL
psql sleepquest < dump.sql
```

---

## Monitoring & Maintenance

### Health Checks

**Backend Health Endpoint:**
```python
# server/app.py
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
```

**Monitor:**
```bash
curl http://localhost:5000/health
```

### Logging

**Configure Logging:**
```python
# server/app.py
import logging

logging.basicConfig(
    filename='/var/log/sleep-quest/app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)
```

**View Logs:**
```bash
tail -f /var/log/sleep-quest/app.log
```

### Performance Monitoring

**Install monitoring tools:**
```bash
pip install flask-monitoring-dashboard
```

**Add to app.py:**
```python
from flask_monitoringdashboard import bind
bind(app)
```

Access dashboard at `/dashboard`

---

## Troubleshooting

### Backend Won't Start

**Check logs:**
```bash
sudo journalctl -u sleep-quest -n 50
```

**Common issues:**
- Port 5000 already in use: `sudo lsof -i :5000`
- Missing dependencies: `pip install -r requirements.txt`
- Database permissions: `chmod 664 database.db`

### Frontend Build Fails

**Clear cache:**
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

### CORS Errors

**Update server/app.py:**
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://your-domain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})
```

### Database Locked

**SQLite specific:**
```bash
# Check for locks
fuser database.db

# Kill locking process
kill -9 <PID>
```

---

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Enable HTTPS (SSL certificate)
- [ ] Set DEBUG=False in production
- [ ] Use environment variables for secrets
- [ ] Implement rate limiting
- [ ] Regular security updates
- [ ] Database backups automated
- [ ] Firewall configured (allow only 80, 443)
- [ ] Strong password policy
- [ ] SQL injection prevention (parameterized queries)

---

## Performance Optimization

### Backend
- Use Gunicorn with multiple workers
- Enable gzip compression
- Cache static responses
- Database indexing (already done)

### Frontend
- Enable React production build
- Use CDN for static assets
- Lazy load components
- Optimize images

### Nginx
```nginx
# Enable gzip
gzip on;
gzip_types text/plain text/css application/json application/javascript;

# Cache static files
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

## Scaling Considerations

### Horizontal Scaling
- Load balancer (Nginx/HAProxy)
- Multiple backend instances
- Shared database (PostgreSQL)
- Redis for session storage

### Vertical Scaling
- Increase server resources (CPU/RAM)
- Optimize database queries
- Use connection pooling

---

**Deployment Version:** 1.0  
**Last Updated:** 2025-11-22  
**Supported Platforms:** Linux, macOS, Windows (development)
