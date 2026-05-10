#!/bin/bash

# Duty System Build and Deployment Script

set -e  # Exit on error

echo "🔨 Building Duty System..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "🔄 Running migrations..."
python manage.py migrate

# Create superuser (optional)
if [ "$CREATE_SUPERUSER" = "true" ]; then
    echo "👤 Creating superuser..."
    python manage.py createsuperuser --noinput \
        --username "$DJANGO_SUPERUSER_USERNAME" \
        --email "$DJANGO_SUPERUSER_EMAIL"
fi

echo "✅ Build complete! You can now run the server:"
echo "   gunicorn backend.wsgi:application --bind 0.0.0.0:8000"
