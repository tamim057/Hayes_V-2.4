# Duty System - Discord Integration

A Django-based duty tracking system that monitors user duty status and sends real-time reports to Discord.

## Features

- **Real-time Duty Tracking**: Track when users go on/off duty
- **Session Timing**: Automatic calculation of session duration
- **Discord Integration**: Real-time notifications via Discord webhooks
- **Daily Reset**: Automatic daily statistics reset (customizable timezone)
- **Bell System**: Reminder system with grace period
- **Django Admin**: Full admin interface for data management

## Tech Stack

- Django 6.0.5
- SQLite3 (default, swappable for production DBs)
- Gunicorn (production server)
- WhiteNoise (static file serving)
- Discord API

## Installation

### Prerequisites

- Python 3.9+
- pip or conda
- Virtual environment (recommended)

### Setup

1. **Clone and navigate to project**
   ```bash
   cd duty_system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

Access the application at `http://localhost:8000`

## API Endpoints

### POST /api/login/
Authenticate user
```json
{
  "user_id": "123456789"
}
```

### POST /api/on/
Mark user as on-duty
```json
{
  "user_id": "123456789"
}
```

### POST /api/off/
Mark user as off-duty
```json
{
  "user_id": "123456789"
}
```

### POST /api/bell/
Acknowledge bell notification
```json
{
  "user_id": "123456789"
}
```

### GET /api/status/?user_id=123456789
Get user's current status

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Discord Webhook
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Configuration
TIME_ZONE=Asia/Dhaka
BELL_TIME=15
GRACE_PERIOD=10
```

## Admin Panel

Access the Django admin at `/admin/` using your superuser credentials.

Manage:
- User duty records
- Reset statistics
- View duty history

## Deployment

### Using Gunicorn

```bash
gunicorn backend.wsgi:application --bind 0.0.0.0:8000
```

### Build Script

Run the build script for automatic setup:
```bash
./build.sh
```

## Project Structure

```
duty_system/
├── backend/           # Django project settings
│   ├── settings.py   # Configuration
│   ├── urls.py       # URL routing
│   └── wsgi.py       # WSGI config
├── core/             # Main application
│   ├── models.py     # Database models
│   ├── views.py      # API endpoints
│   ├── admin.py      # Admin configuration
│   └── urls.py       # App-level routing
├── templates/        # HTML templates
├── static/          # Static assets
├── manage.py        # Django CLI
└── requirements.txt # Dependencies
```

## Security Notes

⚠️ **Important Security Practices:**

- Always set `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Configure `ALLOWED_HOSTS` properly
- Never commit `.env` file to version control
- Use HTTPS in production
- Implement API authentication/rate limiting
- Regularly backup your database

## Logging

The application logs errors and important events. Check logs for:
- Webhook failures
- JSON parsing errors
- Database issues
- Unexpected exceptions

## Troubleshooting

### Discord webhook not working
- Verify `DISCORD_WEBHOOK_URL` in `.env` is correct
- Check Discord server permissions
- Review application logs

### Database errors
- Run migrations: `python manage.py migrate`
- Check database file permissions

### Static files not loading
- Collect static files: `python manage.py collectstatic`
- Verify STATIC_ROOT directory

## Support

For issues or questions, check the application logs or Django error pages in development mode.

## License

Proprietary - All rights reserved
