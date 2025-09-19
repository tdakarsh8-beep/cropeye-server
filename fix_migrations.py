#!/usr/bin/env python
"""
Fix migration dependency issues by creating a clean migration state.
This script handles the 'users' app migration dependency problem.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection

def fix_migration_dependencies():
    """Fix migration dependency issues."""
    print("🔧 Fixing migration dependency issues...")
    
    try:
        # First, let's check if the database is empty
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_migrations;")
            migration_count = cursor.fetchone()[0]
            
        if migration_count == 0:
            print("📊 Database is empty, creating initial migration state...")
            
            # Create the django_migrations table manually
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS django_migrations (
                        id SERIAL PRIMARY KEY,
                        app VARCHAR(255) NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        applied TIMESTAMP WITH TIME ZONE NOT NULL
                    );
                """)
                
                # Insert initial migrations for core Django apps
                initial_migrations = [
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
                
                for app, name in initial_migrations:
                    cursor.execute("""
                        INSERT INTO django_migrations (app, name, applied) 
                        VALUES (%s, %s, NOW())
                        ON CONFLICT DO NOTHING;
                    """, [app, name])
                    
            print("✅ Initial migration state created!")
            
        # Now try to run migrations
        print("📊 Running migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrations successful!")
        return True
        
    except Exception as e:
        print(f"❌ Migration fix failed: {e}")
        
        try:
            # Last resort: try to create tables directly
            print("🔄 Attempting to create tables directly...")
            execute_from_command_line(['manage.py', 'migrate', '--run-syncdb', '--noinput'])
            print("✅ Direct table creation successful!")
            return True
        except Exception as e2:
            print(f"❌ All migration attempts failed: {e2}")
            return False

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'farm_management.settings_production')
    django.setup()
    
    success = fix_migration_dependencies()
    if not success:
        print("💥 Migration fix failed!")
        sys.exit(1)
    else:
        print("🎉 Migration fix successful!")
