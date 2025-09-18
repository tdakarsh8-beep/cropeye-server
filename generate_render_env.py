#!/usr/bin/env python3
"""
Generate Render environment variables locally.
This script creates a local .env.render file with your actual credentials.
DO NOT commit the generated .env.render file to Git.
"""

import secrets
import string

def generate_secret_key():
    """Generate a secure Django secret key."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    return ''.join(secrets.choice(alphabet) for _ in range(50))

def main():
    print("🔧 Generating Render Environment Variables")
    print("=" * 50)
    print()
    
    # Your actual credentials
    env_content = f"""# Render Environment Variables - DO NOT COMMIT TO GIT
# Copy these to your Render web service environment variables

# Django Configuration
DEBUG=False
SECRET_KEY={generate_secret_key()}
DJANGO_SETTINGS_MODULE=farm_management.settings_production
ALLOWED_HOSTS=*.onrender.com,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=https://*.onrender.com,http://localhost:3000

# Database Configuration (Your PostgreSQL credentials)
DB_NAME=farm_management_l1wj
DB_USER=farm_management_l1wj_user
DB_PASSWORD=DySO3fcTFjb8Rgp9IZIxGYgLZ7KxwmjL
DB_HOST=dpg-d3657g3ipnbc73a0iv3g-a.oregon-postgres.render.com
DB_PORT=5432

# Redis Configuration (Your Redis credentials)
REDIS_URL=redis://redis-12784.c265.us-east-1-2.ec2.redns.redis-cloud.com:12784
CELERY_BROKER_URL=redis://redis-12784.c265.us-east-1-2.ec2.redns.redis-cloud.com:12784
CELERY_RESULT_BACKEND=redis://redis-12784.c265.us-east-1-2.ec2.redns.redis-cloud.com:12784

# Email Configuration (Optional - add your email settings)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<your-email>
EMAIL_HOST_PASSWORD=<your-app-password>

# Frontend URL (Update when you deploy frontend)
FRONTEND_URL=https://your-frontend-app.onrender.com
"""
    
    # Write to local file
    with open('.env.render', 'w') as f:
        f.write(env_content)
    
    print("✅ Generated .env.render file with your credentials")
    print()
    print("📋 Your Environment Variables (copy these to Render web service):")
    print()
    print(env_content)
    print()
    print("📝 Next Steps:")
    print("1. Go to [render.com](https://render.com) and sign in")
    print("2. Click 'New +' → 'Web Service'")
    print("3. Connect your GitHub repository")
    print("4. Configure the web service:")
    print("   - Name: farm-management-web")
    print("   - Environment: Docker")
    print("   - Dockerfile Path: ./Dockerfile")
    print("   - Plan: Free or Starter")
    print("5. Add the above environment variables to your web service")
    print("6. Click 'Create Web Service'")
    print("7. Wait for deployment to complete")
    print()
    print("🔗 Your Services:")
    print("✅ PostgreSQL: farm-management-db (Ready)")
    print("✅ Redis: arm-management-redis (Ready)")
    print("⏳ Web Service: farm-management-web (To be created)")
    print()
    print("🎉 Once deployed, your app will be available at:")
    print("   https://farm-management-web.onrender.com")
    print()
    print("⚠️  IMPORTANT: .env.render file is NOT committed to Git for security!")

if __name__ == "__main__":
    main()
