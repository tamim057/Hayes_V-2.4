#!/bin/bash
# Quick Deployment Script - Run this on your production server

set -e

echo "🚀 Duty System - Production Deployment"
echo "======================================"
echo ""

# Step 1: Environment Setup
echo "📦 Step 1: Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Step 2: Environment Configuration
echo "⚙️ Step 2: Checking .env configuration..."
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and update with production values."
    exit 1
fi

# Check required variables
required_vars=("SECRET_KEY" "DISCORD_WEBHOOK_URL" "ALLOWED_HOSTS")
for var in "${required_vars[@]}"; do
    if ! grep -q "^$var=" .env; then
        echo "❌ Missing $var in .env"
        exit 1
    fi
done
echo "✅ .env configuration verified"
echo ""

# Step 3: Database
echo "🗄️ Step 3: Initializing database..."
python manage.py migrate
echo "✅ Database migrations applied"
echo ""

# Step 4: Static Files
echo "📁 Step 4: Collecting static files..."
python manage.py collectstatic --noinput
echo "✅ Static files collected"
echo ""

# Step 5: Verification
echo "🔍 Step 5: Running deployment checks..."
python manage.py check --deploy
echo "⚠️  Expected warnings about HTTPS - these are fine until you set up SSL"
echo ""

# Step 6: Create Superuser (optional)
read -p "Create superuser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python manage.py createsuperuser
fi
echo ""

echo "✅ Deployment preparation complete!"
echo ""
echo "📝 Next steps:"
echo "1. Start Gunicorn:"
echo "   gunicorn backend.wsgi:application --bind 0.0.0.0:8000"
echo ""
echo "2. (Optional) Configure Nginx reverse proxy"
echo "3. (Recommended) Set up SSL/HTTPS certificate"
echo "4. Test endpoints:"
echo "   curl http://localhost:8000/admin/"
echo "   curl -X POST http://localhost:8000/api/login/ -H 'Content-Type: application/json' -d '{\"user_id\": \"test123\"}'"
echo ""
echo "📚 Read DEPLOYMENT.md for detailed instructions"
echo ""
