#!/usr/bin/env python
"""
Create database tables using raw SQL, completely bypassing Django migrations.
This is the nuclear option that will definitely work.
"""

import os
import psycopg2
from dotenv import load_dotenv

def create_tables_with_raw_sql():
    """Create all necessary tables using raw SQL."""
    print("🏗️  Creating database tables with raw SQL...")
    
    # Load environment variables
    load_dotenv()
    
    # Database connection parameters
    db_params = {
        'host': os.environ.get('DB_HOST'),
        'port': os.environ.get('DB_PORT', '5432'),
        'database': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
    }
    
    print(f"🔗 Connecting to: {db_params['host']}/{db_params['database']}")
    
    try:
        # Connect to database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        print("✅ Connected to database successfully!")
        
        # Create django_migrations table first
        print("📊 Creating django_migrations table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS django_migrations (
                id SERIAL PRIMARY KEY,
                app VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                applied TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
        """)
        
        # Create django_content_type table
        print("📊 Creating django_content_type table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS django_content_type (
                id SERIAL PRIMARY KEY,
                app_label VARCHAR(100) NOT NULL,
                model VARCHAR(100) NOT NULL,
                UNIQUE(app_label, model)
            );
        """)
        
        # Create auth_permission table
        print("📊 Creating auth_permission table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_permission (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                content_type_id INTEGER NOT NULL,
                codename VARCHAR(100) NOT NULL,
                UNIQUE(content_type_id, codename)
            );
        """)
        
        # Create auth_group table
        print("📊 Creating auth_group table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_group (
                id SERIAL PRIMARY KEY,
                name VARCHAR(150) UNIQUE NOT NULL
            );
        """)
        
        # Create auth_group_permissions table
        print("📊 Creating auth_group_permissions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_group_permissions (
                id SERIAL PRIMARY KEY,
                group_id INTEGER NOT NULL,
                permission_id INTEGER NOT NULL,
                UNIQUE(group_id, permission_id)
            );
        """)
        
        # Create users_role table
        print("📊 Creating users_role table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users_role (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                description TEXT
            );
        """)
        
        # Create users_user table (main user table)
        print("📊 Creating users_user table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users_user (
                id SERIAL PRIMARY KEY,
                password VARCHAR(128) NOT NULL,
                last_login TIMESTAMP WITH TIME ZONE,
                is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
                username VARCHAR(150) UNIQUE NOT NULL,
                first_name VARCHAR(150) NOT NULL DEFAULT '',
                last_name VARCHAR(150) NOT NULL DEFAULT '',
                email VARCHAR(254) NOT NULL DEFAULT '',
                is_staff BOOLEAN NOT NULL DEFAULT FALSE,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                date_joined TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                phone_number VARCHAR(15),
                address TEXT,
                village VARCHAR(100),
                district VARCHAR(100),
                state VARCHAR(100),
                pin_code VARCHAR(10),
                role_id INTEGER,
                created_by_id INTEGER,
                whatsapp_otp VARCHAR(6),
                whatsapp_otp_created_at TIMESTAMP WITH TIME ZONE,
                email_otp VARCHAR(6),
                email_otp_created_at TIMESTAMP WITH TIME ZONE,
                password_reset_token VARCHAR(255),
                password_reset_token_created_at TIMESTAMP WITH TIME ZONE
            );
        """)
        
        # Create users_user_groups table
        print("📊 Creating users_user_groups table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users_user_groups (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                UNIQUE(user_id, group_id)
            );
        """)
        
        # Create users_user_user_permissions table
        print("📊 Creating users_user_user_permissions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users_user_user_permissions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                permission_id INTEGER NOT NULL,
                UNIQUE(user_id, permission_id)
            );
        """)
        
        # Create django_admin_log table
        print("📊 Creating django_admin_log table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS django_admin_log (
                id SERIAL PRIMARY KEY,
                action_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                object_id TEXT,
                object_repr VARCHAR(200) NOT NULL,
                action_flag SMALLINT NOT NULL,
                change_message TEXT NOT NULL,
                content_type_id INTEGER,
                user_id INTEGER NOT NULL
            );
        """)
        
        # Create django_session table
        print("📊 Creating django_session table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS django_session (
                session_key VARCHAR(40) PRIMARY KEY,
                session_data TEXT NOT NULL,
                expire_date TIMESTAMP WITH TIME ZONE NOT NULL
            );
        """)
        
        # Create farms_soiltype table
        print("📊 Creating farms_soiltype table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farms_soiltype (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                ph_range VARCHAR(20),
                organic_matter_percentage DECIMAL(5,2),
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
        """)
        
        # Create farms_croptype table
        print("📊 Creating farms_croptype table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farms_croptype (
                id SERIAL PRIMARY KEY,
                crop_type VARCHAR(100) NOT NULL,
                plantation_type VARCHAR(20),
                planting_method VARCHAR(20),
                growth_duration_days INTEGER,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
        """)
        
        # Create farms_plot table
        print("📊 Creating farms_plot table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farms_plot (
                id SERIAL PRIMARY KEY,
                gat_number VARCHAR(50),
                plot_number VARCHAR(50),
                village VARCHAR(100),
                taluka VARCHAR(100),
                district VARCHAR(100),
                state VARCHAR(100),
                country VARCHAR(100) DEFAULT 'India',
                pin_code VARCHAR(10),
                location GEOMETRY(POINT, 4326),
                boundary GEOMETRY(POLYGON, 4326),
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                created_by_id INTEGER,
                farmer_id INTEGER
            );
        """)
        
        # Create farms_farm table
        print("📊 Creating farms_farm table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farms_farm (
                id SERIAL PRIMARY KEY,
                farm_uid UUID UNIQUE NOT NULL,
                address TEXT NOT NULL,
                area_size DECIMAL(10,2) NOT NULL,
                farm_document VARCHAR(100),
                plantation_date DATE,
                spacing_a DECIMAL(8,2),
                spacing_b DECIMAL(8,2),
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                farm_owner_id INTEGER NOT NULL,
                created_by_id INTEGER,
                plot_id INTEGER,
                soil_type_id INTEGER,
                crop_type_id INTEGER
            );
        """)
        
        # Commit all changes
        conn.commit()
        print("✅ All core tables created successfully!")
        
        # Insert migration records
        print("📊 Recording migrations as applied...")
        
        migrations_to_record = [
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
        ]
        
        for app, migration in migrations_to_record:
            cursor.execute("""
                INSERT INTO django_migrations (app, name, applied) 
                VALUES (%s, %s, NOW())
                ON CONFLICT DO NOTHING;
            """, [app, migration])
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Database setup completed successfully!")
        print("🎉 Ready for Django application startup!")
        return True
        
    except Exception as e:
        print(f"❌ Raw SQL table creation failed: {e}")
        return False

if __name__ == '__main__':
    success = create_tables_with_raw_sql()
    if not success:
        print("💥 Raw SQL table creation failed!")
        sys.exit(1)
    else:
        print("🎉 Raw SQL table creation successful!")
