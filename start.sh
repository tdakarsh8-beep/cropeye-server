#!/bin/bash

# Exit on any error
set -e

echo "🚀 Starting Django application..."

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
python manage.py check --database default --deploy

# Run migrations with retry logic
echo "📊 Running database migrations..."
python create_initial_migration.py || {
    echo "❌ Initial migration creation failed, trying fallback..."
    python fix_migrations.py || {
        echo "❌ Migration fix script failed, trying manual approach..."
        python manage.py migrate --fake-initial --noinput || {
            echo "❌ All migration attempts failed!"
            exit 1
        }
    }
}

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (optional)
echo "👤 Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('Creating superuser...')
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
" || echo "⚠️ Superuser creation skipped"

# Start the application
echo "🌐 Starting Gunicorn server..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 3 --timeout 120 --access-logfile - --error-logfile - farm_management.wsgi:application
