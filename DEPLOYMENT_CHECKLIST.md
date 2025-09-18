# 🚀 Render Deployment Checklist

## Pre-Deployment Setup

- [ ] **GitHub Repository**: Code is pushed to GitHub
- [ ] **Dockerfile**: Present and working
- [ ] **Requirements**: All dependencies listed in `requirements_production.txt`
- [ ] **Environment Variables**: Documented and ready

## Step 1: Create PostgreSQL Database

- [ ] Go to [render.com](https://render.com) and sign in
- [ ] Click "New +" → "PostgreSQL"
- [ ] Set name: `farm-management-db`
- [ ] Set database: `farm_management`
- [ ] Choose plan: `Free` or `Starter`
- [ ] Select region
- [ ] Click "Create Database"
- [ ] Wait for database to be ready
- [ ] **Copy connection details** (host, port, password)

## Step 2: Create Redis Cache

- [ ] Click "New +" → "Redis"
- [ ] Set name: `farm-management-redis`
- [ ] Choose plan: `Free` or `Starter`
- [ ] Select same region as database
- [ ] Click "Create Redis"
- [ ] Wait for Redis to be ready
- [ ] **Copy connection string**

## Step 3: Deploy Web Service

- [ ] Click "New +" → "Web Service"
- [ ] Connect GitHub repository
- [ ] Set name: `farm-management-web`
- [ ] Set environment: `Docker`
- [ ] Set Dockerfile path: `./Dockerfile`
- [ ] Choose plan: `Free` or `Starter`
- [ ] Select same region as other services

## Step 4: Configure Environment Variables

### Required Variables
- [ ] `DEBUG=False`
- [ ] `SECRET_KEY=<generated-secret-key>`
- [ ] `DJANGO_SETTINGS_MODULE=farm_management.settings_production`
- [ ] `DB_NAME=farm_management`
- [ ] `DB_USER=postgres`
- [ ] `DB_PASSWORD=<your-database-password>`
- [ ] `DB_HOST=<your-database-host>`
- [ ] `DB_PORT=<your-database-port>`
- [ ] `REDIS_URL=<your-redis-connection-string>`
- [ ] `CELERY_BROKER_URL=<your-redis-connection-string>`
- [ ] `CELERY_RESULT_BACKEND=<your-redis-connection-string>`
- [ ] `ALLOWED_HOSTS=*.onrender.com,localhost,127.0.0.1`
- [ ] `CORS_ALLOWED_ORIGINS=https://*.onrender.com,http://localhost:3000`

### Optional Variables
- [ ] `EMAIL_HOST=smtp.gmail.com`
- [ ] `EMAIL_PORT=587`
- [ ] `EMAIL_USE_TLS=True`
- [ ] `EMAIL_HOST_USER=<your-email>`
- [ ] `EMAIL_HOST_PASSWORD=<your-app-password>`
- [ ] `FRONTEND_URL=https://your-frontend-app.onrender.com`

## Step 5: Deploy and Test

- [ ] Click "Create Web Service"
- [ ] Wait for deployment to complete
- [ ] Check build logs for errors
- [ ] Test application URL
- [ ] Verify database connection
- [ ] Test API endpoints
- [ ] Check health endpoint: `/api/health/`

## Step 6: Post-Deployment

- [ ] Create superuser (optional)
- [ ] Test admin panel
- [ ] Verify all features work
- [ ] Set up monitoring (optional)
- [ ] Configure custom domain (optional)

## Troubleshooting

### Common Issues
- [ ] **Build fails**: Check Dockerfile and requirements
- [ ] **Database connection error**: Verify credentials and host
- [ ] **Application crashes**: Check logs and environment variables
- [ ] **Static files not loading**: Verify collectstatic in Dockerfile

### Getting Help
- [ ] Check Render documentation
- [ ] Review application logs
- [ ] Test locally with similar config
- [ ] Check Django settings

## Success Criteria

- [ ] Application loads without errors
- [ ] Database connection works
- [ ] API endpoints respond correctly
- [ ] Admin panel accessible
- [ ] Health check returns 200 OK

## Cost Monitoring

### Free Plan Limits
- [ ] Web service sleeps after 15 min inactivity
- [ ] Database: 1GB storage limit
- [ ] Redis: 25MB memory limit
- [ ] Build time: 90 min/month

### Upgrade Considerations
- [ ] Monitor resource usage
- [ ] Consider Starter plan if hitting limits
- [ ] Set up alerts for resource usage

---

**🎉 Congratulations! Your Django application is now deployed on Render!**

**Next Steps:**
1. Deploy your frontend (if applicable)
2. Set up custom domain
3. Configure monitoring and backups
4. Set up CI/CD pipeline
