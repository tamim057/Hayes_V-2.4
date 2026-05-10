# Render.com Deployment Guide

Complete guide to deploy your Duty System on Render.com

## Prerequisites

- Render.com account (free tier available)
- GitHub repository with your code pushed
- Discord webhook URL ready

## ✅ Ready-to-Deploy Files (Already Configured)

Your project now includes Render-specific configuration:

```
✅ runtime.txt        - Python version specification
✅ Procfile           - Application start command
✅ render.yaml        - Render-specific configuration
✅ .env.example       - Environment variables template
```

---

## 📋 Deployment Steps

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Add Render.com configuration"
git push origin main
```

### Step 2: Connect to Render.com

1. Go to [render.com](https://render.com)
2. Sign up or log in
3. Click **"New +"** → **"Web Service"**
4. Select **"Build and deploy from a Git repository"**
5. Click **"Connect GitHub account"** (if not already connected)
6. Search for your `duty_system` repository
7. Click **"Connect"**

### Step 3: Configure Deployment Settings

**Name**: `duty-system` (or any name you prefer)

**Environment**: Select `Python 3`

**Build Command**: 
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

**Start Command**: 
```bash
gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT
```

**Instance Type**: Free tier (recommended for testing)

### Step 4: Add Environment Variables

Click **"Advanced"** → **"Add Secret File"** or **"Environment"**

Add these variables:

| Variable | Value | Example |
|----------|-------|---------|
| `SECRET_KEY` | Your secure key | `F0HkcZxDtb~#U>NE8x]E]a{...` |
| `DEBUG` | `False` | `False` |
| `ALLOWED_HOSTS` | Your Render domain | `duty-system.onrender.com` |
| `DISCORD_WEBHOOK_URL` | Your webhook URL | `https://discord.com/api/webhooks/...` |
| `TIME_ZONE` | `Asia/Dhaka` | `Asia/Dhaka` |
| `BELL_TIME` | `15` | `15` |
| `GRACE_PERIOD` | `10` | `10` |

**Getting your Render domain**: After deployment, it will be `https://duty-system.onrender.com` (replace with your service name)

### Step 5: Deploy

Click **"Create Web Service"**

Render will:
1. ✅ Clone your repository
2. ✅ Install dependencies from `requirements.txt`
3. ✅ Run collectstatic for static files
4. ✅ Start Gunicorn with your application
5. ✅ Assign a free SSL certificate

**Deployment takes 2-5 minutes** - watch the logs in real-time!

### Step 6: Verify Deployment

Once deployment completes:

1. **Check homepage**: `https://duty-system.onrender.com/`
   - Should show a simple page or admin login

2. **Check admin panel**: `https://duty-system.onrender.com/admin/`
   - Login with superuser credentials (if you created one)

3. **Test API**:
   ```bash
   curl -X POST https://duty-system.onrender.com/api/login/ \
     -H "Content-Type: application/json" \
     -d '{"user_id":"test123"}'
   ```
   Should return: `{"ok": true}`

---

## ⚠️ Potential Issues on Render.com

### Issue 1: "ModuleNotFoundError" during build

**Error Message**: `ModuleNotFoundError: No module named 'django'`

**Solution**:
- ✅ Already fixed - `requirements.txt` is properly configured
- Make sure all dependencies are in `requirements.txt`

### Issue 2: Database Error - "db.sqlite3 not found"

**Error Message**: `django.db.utils.OperationalError: unable to open database file`

**Why**: SQLite on Render.com has file system issues (ephemeral - files are deleted on redeploy)

**Solution Options**:

**Option A: Switch to PostgreSQL (Recommended)**

1. In Render dashboard, create a **PostgreSQL database**:
   - Click **"New +"** → **"PostgreSQL"**
   - Choose free tier
   - Copy the connection string

2. Update `.env` on Render with:
   ```
   DATABASE_URL=<paste-the-connection-string-here>
   ```

3. Install PostgreSQL driver:
   ```bash
   pip install psycopg2-binary
   pip freeze > requirements.txt
   git push origin main  # Redeploy
   ```

4. Add to `settings.py` if not already:
   ```python
   import dj_database_url
   DATABASES = {
       'default': dj_database_url.config(default='sqlite:///db.sqlite3')
   }
   ```

**Option B: Keep SQLite (Temporary/Testing Only)**
- SQLite works but loses data on redeploy
- Fine for testing, not for production
- Data resets every deploy

### Issue 3: Static Files Not Loading

**Error**: CSS/Images return 404

**Why**: WhiteNoise middleware needs proper configuration

**Solution**:
- ✅ Already configured in `settings.py`
- Make sure static files are in `/static/` directory
- Run: `python manage.py collectstatic --noinput`
- This is done automatically by our build command

### Issue 4: Discord Webhook Fails (Connection Error)

**Error**: `requests.exceptions.RequestException`

**Solutions**:
1. Verify webhook URL is correct in environment variable
2. Check Discord server hasn't changed/deleted the webhook
3. Verify webhook token is valid
4. Check logs: Click service → **"Logs"** tab

### Issue 5: Timeout During Build (Build takes >15 min)

**Error**: Build times out

**Solutions**:
- ✅ Unlikely - dependencies are minimal
- If it happens, check `requirements.txt` for large packages
- Use `pip install --no-cache-dir` in build command

### Issue 6: Environment Variables Not Loading

**Error**: `KeyError: 'SECRET_KEY'` or blank values

**Solutions**:
1. Verify all variables are added in Render dashboard
2. Click **"Restart"** after adding variables
3. Check variable names match exactly: `SECRET_KEY`, `DEBUG`, etc.
4. Use `python-dotenv` with `.env` file (for local testing only)

---

## 🔧 Database Setup on Render.com

### Initial Database Setup (One-time)

After deployment, run migrations:

1. In Render dashboard, go to your Web Service
2. Click **"Shell"** tab
3. Run:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. Create superuser when prompted:
   ```
   Username: admin
   Email: your-email@example.com
   Password: (enter strong password)
   ```

### PostgreSQL Connection (Recommended)

**In Render Dashboard**:

1. Create PostgreSQL service
2. Copy connection details
3. Add to environment variables:
   ```
   DATABASE_URL=postgresql://user:password@hostname:5432/dbname
   ```

4. Update `requirements.txt`:
   ```bash
   pip install psycopg2-binary dj-database-url
   pip freeze > requirements.txt
   ```

5. Update `settings.py`:
   ```python
   import dj_database_url
   
   DATABASES = {
       'default': dj_database_url.config(
           default='sqlite:///db.sqlite3',
           conn_max_age=600
       )
   }
   ```

---

## 📊 Monitoring Your Deployment

### View Logs
- Dashboard → Your Service → **"Logs"** tab
- Real-time errors and warnings
- Search for specific errors

### Check Health
- Dashboard → Your Service → **"Health"** section
- Shows CPU, memory, network usage
- Alerts if service crashes

### Manual Deployment
- Make code changes
- Push to GitHub
- Render auto-deploys (no manual trigger needed)
- Watch deployment in logs

---

## 🚀 Production Checklist for Render.com

### Before Going Live

- [ ] Database is PostgreSQL (not SQLite)
- [ ] `SECRET_KEY` is secure and stored in environment
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` includes your Render domain
- [ ] Discord webhook URL is valid and secret
- [ ] SSL/HTTPS enabled (automatic on Render)
- [ ] Tested all API endpoints
- [ ] Admin panel accessible
- [ ] Daily reset functionality working
- [ ] Backups configured (if using PostgreSQL)

### During Deployment

- [ ] Watch logs for errors
- [ ] Test homepage loads
- [ ] Test admin login
- [ ] Test API endpoints
- [ ] Send test Discord notification
- [ ] Verify webhook delivers to Discord

### Post-Deployment

- [ ] Monitor application for 24 hours
- [ ] Check logs daily
- [ ] Monitor Discord webhooks
- [ ] Ensure daily reset happens
- [ ] Plan backup strategy

---

## 🆘 Troubleshooting Commands

### Check Application Status
```
Dashboard → Service → Shell:
python manage.py check
```

### View Migrations Status
```
python manage.py showmigrations
```

### Test Discord Webhook
```python
python manage.py shell
>>> import requests, os
>>> url = os.getenv('DISCORD_WEBHOOK_URL')
>>> requests.post(url, json={"content": "Test"})
```

### View Database
```
python manage.py dbshell
```

---

## 💰 Pricing on Render.com

| Plan | Cost | Includes |
|------|------|----------|
| Web Service (Free) | $0 | 750 hours/month, auto-sleep |
| Web Service (Starter) | $7/month | Always-on, 2.5GB RAM |
| PostgreSQL (Free) | $0 | 256 MB, auto-backup |
| PostgreSQL (Standard) | $15/month | 1 GB, daily backups |

**Tip**: Free tier is perfect for testing/development

---

## 📚 Useful Links

- [Render.com Docs](https://render.com/docs)
- [Django on Render](https://render.com/docs/deploy-django)
- [PostgreSQL Setup](https://render.com/docs/databases)
- [Environment Variables](https://render.com/docs/environment-variables)

---

## ✅ Final Checklist

Before pushing to Render:

- [x] `runtime.txt` - Specifies Python 3.11
- [x] `Procfile` - Startup command configured
- [x] `render.yaml` - Deployment config included
- [x] `requirements.txt` - All dependencies listed
- [x] `.env.example` - Template for variables
- [x] `manage.py` - Django management ready
- [x] `settings.py` - Environment variable support
- [ ] All changes committed to Git
- [ ] Code pushed to GitHub
- [ ] Ready to deploy!

---

## 🎉 You're Ready!

Your application is configured for Render.com deployment. Follow the steps above and you'll be live in minutes!

**Questions?** Check the Render docs or application logs for specific error details.
