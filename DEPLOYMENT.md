# Production Deployment Checklist

Complete this checklist before deploying your Duty System to production.

## 🔐 Security Configuration

### Essential (Do Before Deploy)
- [ ] Generate secure SECRET_KEY using `python generate_secret_key.py`
- [ ] Add generated key to production `.env` file
- [ ] Set `DEBUG=False` in production `.env`
- [ ] Configure `ALLOWED_HOSTS` with your actual domain(s)
- [ ] Create `.env.production` separate from version control

### SSL/HTTPS Setup (Highly Recommended)
- [ ] Obtain SSL certificate (Let's Encrypt, AWS, etc.)
- [ ] Configure HTTPS on web server (Nginx, Apache, etc.)
- [ ] Once HTTPS is live, set these in `.env`:
  ```
  SECURE_SSL_REDIRECT=True
  SESSION_COOKIE_SECURE=True
  CSRF_COOKIE_SECURE=True
  SECURE_HSTS_SECONDS=31536000
  SECURE_HSTS_INCLUDE_SUBDOMAINS=True
  SECURE_HSTS_PRELOAD=True
  ```

## 📦 Dependency & Build

- [ ] Install production dependencies: `pip install -r requirements.txt`
- [ ] Install additional deployment package: `pip install gunicorn psycopg2-binary` (for PostgreSQL)
- [ ] Run `./build.sh` to prepare application
- [ ] Verify all migrations: `python manage.py migrate`
- [ ] Collect static files: `python manage.py collectstatic --noinput`

## 🗄️ Database

- [ ] **For Production**: Migrate from SQLite to PostgreSQL/MySQL
  ```bash
  pip install psycopg2-binary  # For PostgreSQL
  ```
  Update `.env`:
  ```
  DATABASE_URL=postgresql://user:password@hostname:5432/dbname
  ```

- [ ] Create database backups strategy
- [ ] Set up automated daily backups
- [ ] Test backup restoration procedure
- [ ] Verify database permissions and security

## 🌐 Web Server Configuration

### Gunicorn Setup
```bash
gunicorn backend.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --worker-class sync \
  --timeout 60 \
  --access-logfile - \
  --error-logfile -
```

### Nginx (Reverse Proxy) - Example Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload";
    add_header X-Content-Type-Options "nosniff";
    add_header X-Frame-Options "DENY";
    add_header X-XSS-Protection "1; mode=block";

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## 📊 Monitoring & Logging

- [ ] Set up application logging (check `/var/log/gunicorn/`)
- [ ] Set up error monitoring (Sentry, New Relic, etc.) - Optional but recommended
- [ ] Monitor Discord webhook deliveries
- [ ] Set up uptime monitoring for API endpoints
- [ ] Create alerts for critical errors

## 🧪 Pre-Deployment Testing

- [ ] Run `python manage.py check --deploy`
- [ ] Test all API endpoints:
  - [ ] POST `/api/login/`
  - [ ] POST `/api/on/`
  - [ ] POST `/api/off/`
  - [ ] POST `/api/bell/`
  - [ ] GET `/api/status/?user_id=test`
- [ ] Test Discord webhook notifications
- [ ] Verify static files are serving correctly
- [ ] Test admin panel access
- [ ] Verify daily reset functionality

## 🚀 Deployment Steps

1. **Prepare Environment**
   ```bash
   # On production server
   git clone <repo> duty_system
   cd duty_system
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Configure .env**
   ```bash
   cp .env.example .env
   # Edit with production values:
   # - Secure SECRET_KEY
   # - DEBUG=False
   # - Real domain in ALLOWED_HOSTS
   # - Discord webhook URL
   # - Database credentials if not SQLite
   ```

3. **Initialize Database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic --noinput
   ```

4. **Start Application**
   - Using Gunicorn: `gunicorn backend.wsgi:application --bind 0.0.0.0:8000`
   - Using systemd service (recommended)
   - Using Docker container

5. **Post-Deployment Verification**
   - Test homepage loads: `curl https://yourdomain.com/`
   - Check admin panel: `https://yourdomain.com/admin/`
   - Test API: `curl -X POST https://yourdomain.com/api/login/ -d '{"user_id":"test"}'`
   - Monitor logs for errors

## 🔄 Maintenance

- [ ] Set up automated backups (daily minimum)
- [ ] Plan regular security updates (Django, dependencies)
- [ ] Review logs weekly for issues
- [ ] Monitor disk space usage
- [ ] Document runbooks for common operations
- [ ] Plan disaster recovery procedure

## 📋 Quick Reference: Environment Variables

### Required for Production
```
SECRET_KEY=<generated-secure-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DISCORD_WEBHOOK_URL=<your-webhook-url>
TIME_ZONE=Asia/Dhaka
BELL_TIME=15
GRACE_PERIOD=10
```

### Optional Security Settings (when using HTTPS)
```
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

## ⚠️ Common Issues & Solutions

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput --clear
```

### Database Connection Error
- Verify `DATABASE_URL` in `.env`
- Check database server is running
- Verify credentials and permissions

### Webhook Not Working
- Verify Discord webhook URL in `.env`
- Check Discord server permissions
- Review application logs for errors

### High Memory Usage
- Reduce Gunicorn worker count
- Check for memory leaks in application

## 📚 Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt SSL Certificates](https://letsencrypt.org/)

---

**Status**: Ready for production once all items are completed ✅
