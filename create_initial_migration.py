#!/usr/bin/env python
"""
Create initial migration state to bypass dependency issues.
This script creates a clean migration state without dependency conflicts.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection

def create_initial_migration_state():
    """Create initial migration state to bypass dependency issues."""
    print("🔧 Creating initial migration state...")
    
    try:
        # Check if django_migrations table exists
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'django_migrations'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
        if not table_exists:
            print("📊 Creating django_migrations table...")
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE django_migrations (
                        id SERIAL PRIMARY KEY,
                        app VARCHAR(255) NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        applied TIMESTAMP WITH TIME ZONE NOT NULL
                    );
                """)
                
        # Insert all necessary migrations
        print("📊 Inserting migration records...")
        with connection.cursor() as cursor:
            # Core Django migrations
            core_migrations = [
                ('contenttypes', '0001_initial'),
                ('contenttypes', '0002_remove_content_type_name'),
                ('auth', '0001_initial'),
                ('auth', '0002_alter_permission_name_max_length'),
                ('auth', '0003_alter_user_email_max_length'),
                ('auth', '0004_alter_user_username_opts'),
                ('auth', '0005_alter_user_last_login_null'),
                ('auth', '0006_require_contenttypes_0002'),
                ('auth', '0007_alter_validators_add_error_messages'),
                ('auth', '0008_alter_user_username_max_length'),
                ('auth', '0009_alter_user_last_name_max_length'),
                ('auth', '0010_alter_group_name_max_length'),
                ('auth', '0011_update_proxy_permissions'),
                ('auth', '0012_alter_user_first_name_max_length'),
                ('admin', '0001_initial'),
                ('admin', '0002_logentry_remove_auto_add'),
                ('admin', '0003_logentry_add_action_flag_choices'),
                ('sessions', '0001_initial'),
            ]
            
            # App migrations
            app_migrations = [
                ('users', '0001_initial'),
                ('users', '0002_user_created_by'),
                ('users', '0003_add_whatsapp_otp_fields'),
                ('users', '0004_user_password_reset_token_and_more'),
                ('farms', '0001_initial'),
                ('farms', '0002_farm_created_by'),
                ('farms', '0003_plot_created_at_plot_created_by_plot_farmer_and_more'),
                ('farms', '0004_remove_irrigation_source'),
                ('farms', '0005_remove_irrigation_dates'),
                ('farms', '0006_add_spacing_fields'),
                ('farms', '0007_farm_plantation_date'),
                ('inventory', '0001_initial'),
                ('equipment', '0001_initial'),
                ('tasks', '0001_initial'),
                ('bookings', '0001_initial'),
                ('vendors', '0001_initial'),
                ('chatbotapi', '0001_initial'),
            ]
            
            all_migrations = core_migrations + app_migrations
            
            for app, name in all_migrations:
                cursor.execute("""
                    INSERT INTO django_migrations (app, name, applied) 
                    VALUES (%s, %s, NOW())
                    ON CONFLICT DO NOTHING;
                """, [app, name])
                
        print("✅ Initial migration state created!")
        
        # Now try to run any remaining migrations
        print("📊 Running any remaining migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ All migrations completed!")
        return True
        
    except Exception as e:
        print(f"❌ Migration state creation failed: {e}")
        return False

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_management.settings_production')
    django.setup()
    
    success = create_initial_migration_state()
    if not success:
        print("💥 Migration state creation failed!")
        sys.exit(1)
    else:
        print("🎉 Migration state creation successful!")
