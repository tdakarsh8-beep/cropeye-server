# CropEye Server - Render Deployment Guide

## 🚀 Quick Deploy to Render

### Prerequisites
- GitHub repository with this code
- Render account
- PostgreSQL database on Render
- Redis Cloud account

### 1. Database Setup
- Create a PostgreSQL database on Render
- Note down the connection details:
  - Hostname
  - Database name
  - Username
  - Password
  - Port (usually 5432)

### 2. Redis Setup
- Create a Redis instance on Redis Cloud
- Note down the connection URL

### 3. Deploy to Render

#### Step 1: Connect GitHub Repository
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select this repository

#### Step 2: Configure Build Settings
- **Build Command**: `pip install -r requirements_production.txt`
- **Start Command**: `gunicorn farm_management.wsgi:application --bind 0.0.0.0:$PORT`

#### Step 3: Set Environment Variables
Copy the variables from `render_env_template.txt` and set them in Render:

**Required Variables:**
```
DEBUG=False
SECRET_KEY=your-secure-secret-key-here
DJANGO_SETTINGS_MODULE=farm_management.settings_production
ALLOWED_HOSTS=*.onrender.com,your-app-name.onrender.com
DB_NAME=your-database-name
DB_USER=your-database-user
DB_PASSWORD=your-database-password
DB_HOST=your-database-host
DB_PORT=5432
REDIS_URL=your-redis-url
CELERY_BROKER_URL=your-redis-url
CELERY_RESULT_BACKEND=your-redis-url
```

#### Step 4: Deploy
1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. The first deployment will run migrations automatically

### 4. Post-Deployment Setup

#### Create Superuser
After deployment, create a superuser by running:
```bash
# Connect to your Render service shell and run:
python manage.py createsuperuser
```

#### Access Your Application
- **Main App**: `https://your-app-name.onrender.com`
- **Admin Panel**: `https://your-app-name.onrender.com/admin/`

### 5. Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `DEBUG` | Django debug mode | Yes |
| `SECRET_KEY` | Django secret key | Yes |
| `DJANGO_SETTINGS_MODULE` | Django settings module | Yes |
| `ALLOWED_HOSTS` | Allowed hostnames | Yes |
| `DB_NAME` | Database name | Yes |
| `DB_USER` | Database username | Yes |
| `DB_PASSWORD` | Database password | Yes |
| `DB_HOST` | Database hostname | Yes |
| `DB_PORT` | Database port | Yes |
| `REDIS_URL` | Redis connection URL | Yes |
| `CELERY_BROKER_URL` | Celery broker URL | Yes |
| `CELERY_RESULT_BACKEND` | Celery result backend | Yes |
| `FRONTEND_URL` | Frontend application URL | No |

### 6. Troubleshooting

#### Common Issues:
1. **Migration Errors**: Ensure all migration files are committed to git
2. **Database Connection**: Verify database credentials and hostname
3. **Static Files**: Static files are handled automatically by WhiteNoise
4. **Redis Connection**: Verify Redis URL is correct

#### Logs:
- Check Render service logs for detailed error messages
- Use Render shell to debug issues

### 7. Local Development

To run locally with the same configuration:
```bash
# Copy environment template
cp render_env_template.txt .env

# Edit .env with your local values
# Then run:
docker-compose up
```

### 8. Features Included

- ✅ User management with roles
- ✅ Farm management with GIS support
- ✅ Equipment tracking
- ✅ Inventory management
- ✅ Task management
- ✅ Booking system
- ✅ Vendor management
- ✅ REST API with JWT authentication
- ✅ Admin interface
- ✅ Redis caching
- ✅ Celery support for background tasks

### 9. API Endpoints

- **Health Check**: `GET /api/health/`
- **Admin Panel**: `/admin/`
- **API Documentation**: `/swagger/` (if enabled)

### 10. Support

For issues or questions:
1. Check the logs in Render dashboard
2. Verify environment variables
3. Test database connectivity
4. Check Redis connection

---

**Happy Deploying! 🎉**
