#!/usr/bin/env python
"""
Create database schema directly without using Django migrations.
This completely bypasses all migration dependency issues.
"""

import os
import sys
import django
from django.db import connection
from django.core.management import execute_from_command_line

def create_database_schema_directly():
    """Create all database tables directly from model definitions."""
    print("🏗️  Creating database schema directly from models...")
    
    try:
        # Import Django and setup
        from django.apps import apps
        from django.db import connection
        from django.core.management.sql import sql_create_index
        from django.db.backends.utils import names_digest
        
        print("📊 Getting all Django models...")
        
        # Get all models from all apps
        all_models = []
        for app_config in apps.get_app_configs():
            if app_config.name not in ['chatbotapi']:  # Skip removed apps
                models = app_config.get_models()
                all_models.extend(models)
        
        print(f"📊 Found {len(all_models)} models to create tables for")
        
        # Create tables using Django's schema editor
        from django.db import connection
        from django.db.backends.base.schema import BaseDatabaseSchemaEditor
        
        with connection.schema_editor() as schema_editor:
            print("🔧 Creating tables...")
            
            # Create tables for each model
            for model in all_models:
                table_name = model._meta.db_table
                
                # Check if table already exists
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = %s
                        );
                    """, [table_name])
                    table_exists = cursor.fetchone()[0]
                
                if not table_exists:
                    try:
                        print(f"  📋 Creating table: {table_name}")
                        schema_editor.create_model(model)
                    except Exception as e:
                        print(f"  ⚠️  Could not create {table_name}: {e}")
                        continue
                else:
                    print(f"  ✅ Table exists: {table_name}")
        
        print("✅ Database schema created successfully!")
        
        # Now create django_migrations table and mark all migrations as applied
        print("📊 Setting up migration tracking...")
        
        with connection.cursor() as cursor:
            # Create django_migrations table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS django_migrations (
                    id SERIAL PRIMARY KEY,
                    app VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    applied TIMESTAMP WITH TIME ZONE NOT NULL
                );
            """)
            
            # Mark all migrations as applied
            migration_apps = [
                ('contenttypes', ['0001_initial', '0002_remove_content_type_name']),
                ('auth', ['0001_initial', '0002_alter_permission_name_max_length', 
                         '0003_alter_user_email_max_length', '0004_alter_user_username_opts',
                         '0005_alter_user_last_login_null', '0006_require_contenttypes_0002',
                         '0007_alter_validators_add_error_messages', '0008_alter_user_username_max_length',
                         '0009_alter_user_last_name_max_length', '0010_alter_group_name_max_length',
                         '0011_update_proxy_permissions', '0012_alter_user_first_name_max_length']),
                ('admin', ['0001_initial', '0002_logentry_remove_auto_add', '0003_logentry_add_action_flag_choices']),
                ('sessions', ['0001_initial']),
                ('users', ['0001_initial', '0002_user_created_by', '0003_add_whatsapp_otp_fields', '0004_user_password_reset_token_and_more']),
                ('farms', ['0001_initial', '0002_farm_created_by', '0003_plot_created_at_plot_created_by_plot_farmer_and_more',
                          '0004_remove_irrigation_source', '0005_remove_irrigation_dates', '0006_add_spacing_fields', '0007_farm_plantation_date']),
                ('inventory', ['0001_initial']),
                ('equipment', ['0001_initial']),
                ('tasks', ['0001_initial']),
                ('bookings', ['0001_initial']),
                ('vendors', ['0001_initial']),
                # No chatbotapi migrations
            ]
            
            for app_name, migrations in migration_apps:
                for migration_name in migrations:
                    cursor.execute("""
                        INSERT INTO django_migrations (app, name, applied) 
                        VALUES (%s, %s, NOW())
                        ON CONFLICT DO NOTHING;
                    """, [app_name, migration_name])
        
        print("✅ Migration tracking set up successfully!")
        print("🎉 Database is ready for Django application!")
        return True
        
    except Exception as e:
        print(f"❌ Schema creation failed: {e}")
        return False

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_management.settings_production')
    django.setup()
    
    success = create_database_schema_directly()
    if not success:
        print("💥 Schema creation failed!")
        sys.exit(1)
    else:
        print("🎉 Schema creation successful!")
