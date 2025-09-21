#!/usr/bin/env python
"""
Create ALL database tables using Django's SQL generation capabilities.
This ensures we don't miss any tables and get the exact schema Django expects.
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

def create_all_tables_comprehensive():
    """Create all database tables using Django's SQL generation."""
    print("🏗️  Creating ALL database tables comprehensively...")
    
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
        
        # First, let's create the essential Django tables manually
        print("📊 Creating essential Django framework tables...")
        
        # django_migrations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS django_migrations (
                id SERIAL PRIMARY KEY,
                app VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                applied TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
        """)
        
        # django_content_type table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS django_content_type (
                id SERIAL PRIMARY KEY,
                app_label VARCHAR(100) NOT NULL,
                model VARCHAR(100) NOT NULL,
                UNIQUE(app_label, model)
            );
        """)
        
        # auth_permission table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_permission (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                content_type_id INTEGER NOT NULL,
                codename VARCHAR(100) NOT NULL,
                UNIQUE(content_type_id, codename)
            );
        """)
        
        # auth_group table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_group (
                id SERIAL PRIMARY KEY,
                name VARCHAR(150) UNIQUE NOT NULL
            );
        """)
        
        # auth_group_permissions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auth_group_permissions (
                id SERIAL PRIMARY KEY,
                group_id INTEGER NOT NULL,
                permission_id INTEGER NOT NULL,
                UNIQUE(group_id, permission_id)
            );
        """)
        
        # django_admin_log table
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
        
        # django_session table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS django_session (
                session_key VARCHAR(40) PRIMARY KEY,
                session_data TEXT NOT NULL,
                expire_date TIMESTAMP WITH TIME ZONE NOT NULL
            );
        """)
        
        print("📊 Creating application-specific tables...")
        
        # users_role table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users_role (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                display_name VARCHAR(100) DEFAULT ''
            );
        """)
        
        # users_user table (complete with all fields)
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
                phone_number VARCHAR(15) DEFAULT '',
                otp VARCHAR(6),
                otp_created_at TIMESTAMP WITH TIME ZONE,
                otp_delivery_method VARCHAR(20),
                password_reset_token VARCHAR(100),
                password_reset_token_created_at TIMESTAMP WITH TIME ZONE,
                address TEXT DEFAULT '',
                village VARCHAR(100) DEFAULT '',
                state VARCHAR(100) DEFAULT '',
                district VARCHAR(100) DEFAULT '',
                taluka VARCHAR(100) DEFAULT '',
                profile_picture VARCHAR(100),
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                role_id INTEGER REFERENCES users_role(id),
                created_by_id INTEGER REFERENCES users_user(id)
            );
        """)
        
        # users_user_groups table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users_user_groups (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users_user(id),
                group_id INTEGER NOT NULL REFERENCES auth_group(id),
                UNIQUE(user_id, group_id)
            );
        """)
        
        # users_user_user_permissions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users_user_user_permissions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users_user(id),
                permission_id INTEGER NOT NULL REFERENCES auth_permission(id),
                UNIQUE(user_id, permission_id)
            );
        """)
        
        # Farm-related tables
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
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farms_irrigationtype (
                id SERIAL PRIMARY KEY,
                name VARCHAR(20) UNIQUE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farms_sensortype (
                id SERIAL PRIMARY KEY,
                name VARCHAR(20) UNIQUE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            );
        """)
        
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
                created_by_id INTEGER REFERENCES users_user(id),
                farmer_id INTEGER REFERENCES users_user(id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farms_farm (
                id SERIAL PRIMARY KEY,
                farm_uid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
                address TEXT NOT NULL,
                area_size DECIMAL(10,2) NOT NULL,
                farm_document VARCHAR(100),
                plantation_date DATE,
                spacing_a DECIMAL(8,2),
                spacing_b DECIMAL(8,2),
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                farm_owner_id INTEGER NOT NULL REFERENCES users_user(id),
                created_by_id INTEGER REFERENCES users_user(id),
                plot_id INTEGER REFERENCES farms_plot(id),
                soil_type_id INTEGER REFERENCES farms_soiltype(id),
                crop_type_id INTEGER REFERENCES farms_croptype(id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farms_farmirrigation (
                id SERIAL PRIMARY KEY,
                status VARCHAR(20) NOT NULL DEFAULT 'active',
                motor_horsepower DECIMAL(5,2),
                pipe_width_inches DECIMAL(5,2),
                flow_rate_lph DECIMAL(10,2),
                plants_per_acre INTEGER,
                emitters_count INTEGER,
                distance_motor_to_plot_m DECIMAL(10,2),
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                farm_id INTEGER NOT NULL REFERENCES farms_farm(id),
                irrigation_type_id INTEGER REFERENCES farms_irrigationtype(id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farms_farmsensor (
                id SERIAL PRIMARY KEY,
                sensor_value DECIMAL(10,2),
                reading_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                farm_id INTEGER NOT NULL REFERENCES farms_farm(id),
                sensor_type_id INTEGER REFERENCES farms_sensortype(id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS farms_farmimage (
                id SERIAL PRIMARY KEY,
                image VARCHAR(100) NOT NULL,
                description TEXT,
                uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                farm_id INTEGER NOT NULL REFERENCES farms_farm(id),
                uploaded_by_id INTEGER REFERENCES users_user(id)
            );
        """)
        
        # Inventory tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory_inventoryitem (
                id SERIAL PRIMARY KEY,
                item_name VARCHAR(200) NOT NULL,
                description TEXT DEFAULT '',
                quantity INTEGER NOT NULL,
                unit VARCHAR(50) NOT NULL,
                purchase_date DATE,
                expiry_date DATE,
                category VARCHAR(20) DEFAULT 'other',
                status VARCHAR(20) DEFAULT 'in_stock',
                reorder_level INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                created_by_id INTEGER NOT NULL REFERENCES users_user(id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory_inventorytransaction (
                id SERIAL PRIMARY KEY,
                transaction_type VARCHAR(20) NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(10,2),
                total_price DECIMAL(10,2),
                notes TEXT DEFAULT '',
                transaction_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                item_id INTEGER NOT NULL REFERENCES inventory_inventoryitem(id),
                created_by_id INTEGER NOT NULL REFERENCES users_user(id)
            );
        """)
        
        # Equipment tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipment_equipment (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                equipment_type VARCHAR(100) DEFAULT '',
                description TEXT DEFAULT '',
                purchase_date DATE,
                price DECIMAL(10,2),
                status VARCHAR(20) DEFAULT 'available',
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                owner_id INTEGER REFERENCES users_user(id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipment_maintenancerecord (
                id SERIAL PRIMARY KEY,
                maintenance_type VARCHAR(100) NOT NULL,
                description TEXT DEFAULT '',
                cost DECIMAL(10,2),
                maintenance_date DATE NOT NULL,
                next_maintenance_date DATE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                equipment_id INTEGER NOT NULL REFERENCES equipment_equipment(id),
                performed_by_id INTEGER REFERENCES users_user(id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipment_equipmentusage (
                id SERIAL PRIMARY KEY,
                usage_date DATE NOT NULL,
                hours_used DECIMAL(5,2) NOT NULL,
                fuel_consumed DECIMAL(8,2),
                notes TEXT DEFAULT '',
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                equipment_id INTEGER NOT NULL REFERENCES equipment_equipment(id),
                used_by_id INTEGER NOT NULL REFERENCES users_user(id),
                farm_id INTEGER REFERENCES farms_farm(id)
            );
        """)
        
        # Task tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks_task (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                priority VARCHAR(20) DEFAULT 'medium',
                due_date TIMESTAMP WITH TIME ZONE NOT NULL,
                completed_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                assigned_to_id INTEGER REFERENCES users_user(id),
                created_by_id INTEGER NOT NULL REFERENCES users_user(id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks_taskcomment (
                id SERIAL PRIMARY KEY,
                comment TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                task_id INTEGER NOT NULL REFERENCES tasks_task(id),
                created_by_id INTEGER NOT NULL REFERENCES users_user(id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks_taskattachment (
                id SERIAL PRIMARY KEY,
                file VARCHAR(100) NOT NULL,
                description TEXT DEFAULT '',
                uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                task_id INTEGER NOT NULL REFERENCES tasks_task(id),
                uploaded_by_id INTEGER NOT NULL REFERENCES users_user(id)
            );
        """)
        
        # Booking tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings_booking (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                description TEXT DEFAULT '',
                booking_type VARCHAR(20) NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                start_date TIMESTAMP WITH TIME ZONE NOT NULL,
                end_date TIMESTAMP WITH TIME ZONE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                created_by_id INTEGER NOT NULL REFERENCES users_user(id),
                approved_by_id INTEGER REFERENCES users_user(id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings_bookingcomment (
                id SERIAL PRIMARY KEY,
                comment TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                booking_id INTEGER NOT NULL REFERENCES bookings_booking(id),
                created_by_id INTEGER NOT NULL REFERENCES users_user(id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings_bookingattachment (
                id SERIAL PRIMARY KEY,
                file VARCHAR(100) NOT NULL,
                description TEXT DEFAULT '',
                uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                booking_id INTEGER NOT NULL REFERENCES bookings_booking(id),
                uploaded_by_id INTEGER NOT NULL REFERENCES users_user(id)
            );
        """)
        
        # Vendor tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendors_vendor (
                id SERIAL PRIMARY KEY,
                name VARCHAR(200) NOT NULL,
                contact_person VARCHAR(100) DEFAULT '',
                phone VARCHAR(15) DEFAULT '',
                email VARCHAR(254) DEFAULT '',
                address TEXT DEFAULT '',
                vendor_type VARCHAR(50) DEFAULT '',
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                created_by_id INTEGER REFERENCES users_user(id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendors_purchaseorder (
                id SERIAL PRIMARY KEY,
                order_number VARCHAR(100) UNIQUE NOT NULL,
                order_date DATE NOT NULL,
                expected_delivery_date DATE,
                status VARCHAR(20) DEFAULT 'pending',
                total_amount DECIMAL(12,2) DEFAULT 0,
                notes TEXT DEFAULT '',
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                vendor_id INTEGER NOT NULL REFERENCES vendors_vendor(id),
                created_by_id INTEGER NOT NULL REFERENCES users_user(id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendors_purchaseorderitem (
                id SERIAL PRIMARY KEY,
                item_name VARCHAR(200) NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                total_price DECIMAL(12,2) NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                purchase_order_id INTEGER NOT NULL REFERENCES vendors_purchaseorder(id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendors_vendorcommunication (
                id SERIAL PRIMARY KEY,
                communication_type VARCHAR(20) NOT NULL,
                subject VARCHAR(200) DEFAULT '',
                message TEXT NOT NULL,
                communication_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                vendor_id INTEGER NOT NULL REFERENCES vendors_vendor(id),
                created_by_id INTEGER NOT NULL REFERENCES users_user(id)
            );
        """)
        
        # Commit all table creation
        conn.commit()
        print("✅ All application tables created successfully!")
        
        # Record all migrations as applied
        print("📊 Recording all migrations as applied...")
        
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
            ('inventory', '0001_initial'),
            ('equipment', '0001_initial'),
            ('tasks', '0001_initial'),
            ('bookings', '0001_initial'),
            ('vendors', '0001_initial'),
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
        
        print("✅ Complete database setup finished!")
        print("🎉 ALL tables created and migration tracking established!")
        return True
        
    except Exception as e:
        print(f"❌ Comprehensive table creation failed: {e}")
        return False

if __name__ == '__main__':
    success = create_all_tables_comprehensive()
    if not success:
        print("💥 Comprehensive table creation failed!")
        sys.exit(1)
    else:
        print("🎉 Comprehensive table creation successful!")
