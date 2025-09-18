# Manual Render Deployment Guide

Since Blueprint deployment requires a paid plan, here's how to deploy your Django application manually on Render for free.

## Step 1: Create PostgreSQL Database

1. **Go to [render.com](https://render.com) and sign in**
2. **Click "New +" → "PostgreSQL"**
3. **Configure the database:**
   - **Name**: `farm-management-db`
   - **Database**: `farm_management`
   - **User**: `postgres` (default)
   - **Plan**: `Free` (or `Starter` if you need more resources)
   - **Region**: Choose closest to your users
4. **Click "Create Database"**
5. **Wait for the database to be ready**
6. **Note down the connection details from the dashboard**

## Step 2: Create Redis Cache

1. **Click "New +" → "Redis"**
2. **Configure Redis:**
   - **Name**: `farm-management-redis`
   - **Plan**: `Free` (or `Starter` if you need more resources)
   - **Region**: Same as your database
3. **Click "Create Redis"**
4. **Wait for Redis to be ready**
5. **Note down the connection details**

## Step 3: Deploy Django Web Service

1. **Click "New +" → "Web Service"**
2. **Connect your GitHub repository**
3. **Configure the web service:**
   - **Name**: `farm-management-web`
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./Dockerfile`
   - **Plan**: `Free` (or `Starter` if you need more resources)
   - **Region**: Same as your database and Redis

## Step 4: Configure Environment Variables

In your web service settings, add these environment variables:

### Database Configuration
```
DB_NAME=farm_management
DB_USER=postgres
DB_PASSWORD=<your-database-password>
DB_HOST=<your-database-host>
DB_PORT=<your-database-port>
```

### Redis Configuration
```
REDIS_URL=<your-redis-connection-string>
CELERY_BROKER_URL=<your-redis-connection-string>
CELERY_RESULT_BACKEND=<your-redis-connection-string>
```

### Django Configuration
```
DEBUG=False
SECRET_KEY=<generate-a-secure-secret-key>
DJANGO_SETTINGS_MODULE=farm_management.settings_production
ALLOWED_HOSTS=*.onrender.com,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=https://*.onrender.com,http://localhost:3000
```

### Email Configuration (Optional)
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<your-email>
EMAIL_HOST_PASSWORD=<your-app-password>
```

### Frontend URL (Update when you deploy frontend)
```
FRONTEND_URL=https://your-frontend-app.onrender.com
```

## Step 5: Deploy

1. **Click "Create Web Service"**
2. **Wait for the deployment to complete**
3. **Check the logs for any errors**
4. **Test your application at the provided URL**

## Step 6: Create Superuser (Optional)

After deployment, you can create a superuser by running:

1. **Go to your web service dashboard**
2. **Click "Shell"**
3. **Run**: `python manage.py createsuperuser`
4. **Follow the prompts to create an admin user**

## Important Notes

### Free Plan Limitations
- **Web Service**: Sleeps after 15 minutes of inactivity
- **Database**: 1GB storage limit
- **Redis**: 25MB memory limit
- **Build Time**: 90 minutes per month

### Security
- Never commit sensitive environment variables to Git
- Use strong passwords for database and secret keys
- Enable HTTPS (automatic on Render)

### Monitoring
- Check logs regularly for errors
- Monitor resource usage
- Set up alerts if needed

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify database credentials
   - Check if database is running
   - Ensure correct host and port

2. **Build Failures**
   - Check Dockerfile syntax
   - Verify all dependencies in requirements_production.txt
   - Check build logs for specific errors

3. **Application Crashes**
   - Check application logs
   - Verify all environment variables are set
   - Test database connectivity

### Getting Help
- Check Render's documentation
- Review application logs
- Test locally with similar configuration

## Next Steps

1. **Deploy your frontend** (if you have one)
2. **Set up custom domain** (optional)
3. **Configure monitoring and alerts**
4. **Set up automated backups** (for paid plans)

## Cost Estimation

### Free Plan
- **Web Service**: Free (with limitations)
- **PostgreSQL**: Free (1GB limit)
- **Redis**: Free (25MB limit)
- **Total**: $0/month

### Starter Plan (if you need more resources)
- **Web Service**: $7/month
- **PostgreSQL**: $7/month
- **Redis**: $7/month
- **Total**: $21/month

This manual deployment approach gives you full control and works with Render's free tier!
