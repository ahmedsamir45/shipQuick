# Koyeb Deployment Guide

Deploy your Django backend to Koyeb with PostgreSQL (Aiven) database.

## Prerequisites

- Koyeb account (sign up at https://www.koyeb.com)
- Aiven PostgreSQL database (already configured)
- Git repository (GitHub, GitLab, or Bitbucket)

## Step 1: Prepare Your Repository

Ensure these files are in your repository:
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Tells Koyeb how to run your app
- ✅ `runtime.txt` - Python version specification
- ✅ `.dockerignore` - Excludes unnecessary files

Your Procfile should contain:
```
web: gunicorn shipping_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
release: python manage.py migrate && python manage.py collectstatic --noinput
```

## Step 2: Deploy to Koyeb

### Via Koyeb Dashboard

1. Go to https://app.koyeb.com
2. Click **Create App**
3. Select **GitHub** (or your Git provider)
4. Choose your repository
5. Configure the deployment:

   **Builder:** Buildpack

   **Build Command:**
   ```bash
   pip install -r requirements.txt
   ```

   **Run Command:**
   ```bash
   gunicorn shipping_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
   ```

## Step 3: Configure Environment Variables

In Koyeb App Settings → Environment Variables, add:

### Required Variables

```env
# Django Settings
SECRET_KEY=your-super-secret-key-here-change-this
DEBUG=False
ALLOWED_HOSTS=.koyeb.app,your-custom-domain.com

# Database (Aiven PostgreSQL)
DB_ENGINE=postgresql
DB_NAME=your-database-name
DB_USER=your-database-user
DB_PASSWORD=your-database-password
DB_HOST=your-database-host.aivencloud.com
DB_PORT=your-database-port
DB_SSLMODE=require

# CORS (Add your Vercel URL after deploying frontend)
CORS_ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-app-git-main.vercel.app

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/shipping_platform.log

# Optional: Address Validation APIs
PRIMARY_ADDRESS_VALIDATOR=usps
USPS_API_KEY=your-key-here
USPS_USER_ID=your-user-id-here
FALLBACK_ADDRESS_VALIDATOR=google
GOOGLE_MAPS_API_KEY=your-key-here
```

### Important Notes

1. **SECRET_KEY**: Generate a new secret key for production:
   ```python
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **ALLOWED_HOSTS**: Use `.koyeb.app` to allow all Koyeb subdomains
   - Or specify exact URL: `your-app-koyeb.app`

3. **CORS_ALLOWED_ORIGINS**: Update with your Vercel frontend URL after deployment

## Step 4: Deploy

1. Click **Deploy**
2. Koyeb will:
   - Build your application
   - Install dependencies
   - Run migrations (via Procfile release command)
   - Collect static files
   - Start Gunicorn server

3. Monitor deployment in the **Logs** tab

## Step 5: Get Your Backend URL

After successful deployment:

1. Go to **Settings** → **Domains**
2. Copy your Koyeb URL: `https://your-app-koyeb.app`
3. This is your backend URL for the frontend

## Step 6: Update Frontend (Vercel)

In your Vercel project environment variables:

```env
VITE_API_BASE_URL=https://your-app-koyeb.app/api
```

Redeploy your Vercel frontend to apply changes.

## Step 7: Update CORS Settings

After getting your Vercel frontend URL:

1. Go to Koyeb → Your App → Settings → Environment Variables
2. Update `CORS_ALLOWED_ORIGINS`:
   ```
   https://your-app.vercel.app,https://your-app-git-main.vercel.app
   ```
3. Redeploy the app to apply changes

## Koyeb-Specific Features

### Auto-Deploy on Git Push

Koyeb automatically redeploys when you push to your repository:
- **Main branch** → Production deployment
- Enable/disable in **Settings** → **Deployments**

### Health Checks

Koyeb automatically monitors your app health. Configure in:
- **Settings** → **Health Checks**
- Default: HTTP GET to `/` every 30 seconds

### Scaling

Koyeb offers auto-scaling:
- **Settings** → **Scaling**
- Configure min/max instances
- Free tier: 1 instance

### Custom Domain

To use a custom domain:

1. Go to **Settings** → **Domains**
2. Click **Add Domain**
3. Enter your domain: `api.yourdomain.com`
4. Add DNS records as instructed:
   - Type: `CNAME`
   - Name: `api` (or `@` for root domain)
   - Value: Your Koyeb app URL
5. Update `ALLOWED_HOSTS` in environment variables

## Static Files

Static files are served by WhiteNoise (already configured):
- CSS, JavaScript, and admin files served automatically
- No additional configuration needed

## Database Migrations

Migrations run automatically on each deployment via Procfile:
```
release: python manage.py migrate && python manage.py collectstatic --noinput
```

To run migrations manually:
1. Go to **Runtime** → **Console**
2. Run: `python manage.py migrate`

## Monitoring & Logs

### View Logs

1. Go to **Logs** tab
2. Filter by:
   - Build logs
   - Runtime logs
   - Error logs

### Metrics

Koyeb provides metrics:
- CPU usage
- Memory usage
- Request count
- Response time

## Troubleshooting

### Build Failures

Check build logs for:
- Missing dependencies in `requirements.txt`
- Python version mismatch
- Build command errors

### Database Connection Errors

Verify:
- All database environment variables are set correctly
- `DB_SSLMODE=require` is set (required for Aiven)
- Aiven database is accessible (check firewall rules)

### CORS Errors

If frontend shows CORS errors:
1. Check `CORS_ALLOWED_ORIGINS` includes exact Vercel URL
2. Ensure no trailing slashes in URLs
3. Verify both HTTP and HTTPS if needed

### Static Files Not Loading

1. Check `collectstatic` ran successfully in logs
2. Verify `STATIC_ROOT` and `STATIC_URL` in settings.py
3. WhiteNoise should be in `MIDDLEWARE` (already configured)

## Environment-Specific Settings

### Development
```env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Production (Koyeb)
```env
DEBUG=False
ALLOWED_HOSTS=.koyeb.app,your-custom-domain.com
CORS_ALLOWED_ORIGINS=https://your-app.vercel.app
```

## Production Checklist

Before deploying to production:

- [ ] Set `DEBUG=False`
- [ ] Generate new `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` with Koyeb domain
- [ ] Set all database environment variables
- [ ] Update `CORS_ALLOWED_ORIGINS` with Vercel URL
- [ ] Test database connection (check Koyeb logs)
- [ ] Verify migrations ran successfully
- [ ] Test API endpoints: `https://your-app-koyeb.app/api/sessions/`
- [ ] Check static files load correctly
- [ ] Monitor logs for errors

## Useful Commands

Generate Django secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Test API endpoint:
```bash
curl https://your-app-koyeb.app/api/sessions/
```

Check database connection:
```bash
python manage.py check --database default
```

## Cost Optimization

Koyeb Free Tier includes:
- 1 free instance
- 1 vCPU
- 512 MB RAM
- 1 GB disk

For production:
- Upgrade to paid plan for better performance
- Enable auto-scaling for traffic spikes
- Monitor usage in dashboard

## Support

- Koyeb Documentation: https://www.koyeb.com/docs
- Koyeb Support: https://www.koyeb.com/support
- Community: https://community.koyeb.com
