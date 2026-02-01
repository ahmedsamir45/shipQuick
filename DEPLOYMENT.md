# ShipQuick Backend Deployment Guide

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 14 or higher
- Linux server (Ubuntu 22.04 recommended)
- Domain name (optional but recommended)

## Step 1: Install PostgreSQL

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## Step 2: Create PostgreSQL Database

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE shipping_db;
CREATE USER shipping_user WITH PASSWORD 'your_strong_password';

# Grant privileges
ALTER ROLE shipping_user SET client_encoding TO 'utf8';
ALTER ROLE shipping_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE shipping_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE shipping_db TO shipping_user;

# Exit psql
\q
```

## Step 3: Clone and Setup Application

```bash
# Clone your repository
git clone <your-repo-url> /var/www/shipping-backend
cd /var/www/shipping-backend

# Copy environment file and configure it
cp .env.production.example .env
nano .env  # Edit with your production settings

# Run deployment script
chmod +x deploy.sh
./deploy.sh
```

## Step 4: Configure Environment Variables

Edit your `.env` file with production values:

```env
SECRET_KEY=<generate-with-python-django>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip

DB_ENGINE=postgresql
DB_NAME=shipping_db
DB_USER=shipping_user
DB_PASSWORD=your_strong_password
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

### Generate Secret Key

```python
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

## Step 5: Create Systemd Service

Create `/etc/systemd/system/shipping-backend.service`:

```ini
[Unit]
Description=ShipQuick Backend (Gunicorn)
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/shipping-backend
Environment="PATH=/var/www/shipping-backend/venv/bin"
ExecStart=/var/www/shipping-backend/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/var/www/shipping-backend/shipping.sock \
    --timeout 120 \
    --access-logfile /var/www/shipping-backend/logs/gunicorn-access.log \
    --error-logfile /var/www/shipping-backend/logs/gunicorn-error.log \
    --log-level info \
    shipping_backend.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable shipping-backend
sudo systemctl start shipping-backend
sudo systemctl status shipping-backend
```

## Step 6: Configure Nginx

Create `/etc/nginx/sites-available/shipping-backend`:

```nginx
upstream shipping_backend {
    server unix:/var/www/shipping-backend/shipping.sock fail_timeout=0;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 10M;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration (use certbot for Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 10M;

    # Static files
    location /static/ {
        alias /var/www/shipping-backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/shipping-backend/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # API endpoints
    location / {
        proxy_pass http://shipping_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/shipping-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Step 7: Setup SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured automatically
sudo certbot renew --dry-run
```

## Step 8: Post-Deployment

```bash
# Create Django superuser
cd /var/www/shipping-backend
source venv/bin/activate
python manage.py createsuperuser

# Check logs
sudo journalctl -u shipping-backend -f  # Follow service logs
tail -f logs/shipping_platform.log       # Application logs
tail -f logs/gunicorn-access.log        # Gunicorn access logs
```

## Maintenance Commands

### Update Application

```bash
cd /var/www/shipping-backend
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart shipping-backend
```

### Database Backup

```bash
# Backup
pg_dump -U shipping_user shipping_db > backup_$(date +%Y%m%d).sql

# Restore
psql -U shipping_user shipping_db < backup_20260201.sql
```

### Monitor Service

```bash
# Check status
sudo systemctl status shipping-backend

# View logs
sudo journalctl -u shipping-backend -n 100

# Restart service
sudo systemctl restart shipping-backend
```

## Troubleshooting

### 502 Bad Gateway

- Check if Gunicorn is running: `sudo systemctl status shipping-backend`
- Check socket file permissions: `ls -la /var/www/shipping-backend/shipping.sock`
- Check Gunicorn logs: `tail -f logs/gunicorn-error.log`

### Database Connection Errors

- Verify PostgreSQL is running: `sudo systemctl status postgresql`
- Test connection: `psql -U shipping_user -d shipping_db -h localhost`
- Check `.env` database credentials

### Static Files Not Loading

- Run `python manage.py collectstatic --noinput`
- Check Nginx static file location in config
- Verify file permissions: `sudo chown -R www-data:www-data staticfiles/`

## Security Checklist

- [x] Set DEBUG=False in production
- [x] Use strong SECRET_KEY
- [x] Configure ALLOWED_HOSTS correctly
- [x] Enable SSL/HTTPS
- [x] Set secure cookie flags
- [x] Configure CORS properly
- [x] Use strong database password
- [x] Enable firewall (ufw)
- [x] Keep system updated
- [x] Regular backups
- [x] Monitor logs

## Performance Optimization

1. **Database Connection Pooling**: Already configured in settings (CONN_MAX_AGE=600)
2. **Gunicorn Workers**: 4 workers (adjust based on CPU cores: 2-4 x CPU cores)
3. **Nginx Caching**: Static files cached for 30 days
4. **Database Indexes**: Already configured in models
5. **Query Optimization**: Use select_related and prefetch_related

## Monitoring

Consider setting up:
- **Sentry** for error tracking
- **New Relic** or **DataDog** for APM
- **Prometheus + Grafana** for metrics
- **ELK Stack** for log aggregation
