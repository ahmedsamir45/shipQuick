#!/bin/bash

# Deployment script for ShipQuick Backend
# This script helps deploy the Django application to production

set -e  # Exit on error

echo "======================================"
echo "ShipQuick Backend Deployment Script"
echo "======================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Please copy .env.production.example to .env and configure it."
    echo "cp .env.production.example .env"
    exit 1
fi

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser (optional, commented out by default)
# echo "Creating superuser..."
# python manage.py createsuperuser

echo "======================================"
echo "Deployment completed successfully!"
echo "======================================"
echo ""
echo "To start the server in production, run:"
echo "gunicorn shipping_backend.wsgi:application --bind 0.0.0.0:8000 --workers 4"
echo ""
echo "Or use systemd service (recommended)"
