from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from .models import Farm, Plot, SoilType, CropType, IrrigationType
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class CompleteFarmerRegistrationService:
    """
    Unified service for complete farmer registration including:
    - Farmer (User) creation
    - Plot creation with geometry
    - Farm creation linking plot and farmer
    - Soil type, crop type, and irrigation setup
    """
    
    @staticmethod
    @transaction.atomic
    def register_complete_farmer(data, field_officer):
        """
        Complete farmer registration in a single atomic transaction
        
        Args:
            data: Dictionary containing all registration data
            field_officer: Field officer creating the registration
            
        Returns:
            Dictionary with created objects and their IDs
        """
        try:
            # Step 1: Create Farmer (User)
            farmer = CompleteFarmerRegistrationService._create_farmer(data.get('farmer', {}), field_officer)
            
            # Step 2: Create Plot (if provided)
            plot = None
            if data.get('plot'):
                plot = CompleteFarmerRegistrationService._create_plot(
                    data['plot'], farmer, field_officer
                )
            
            # Step 3: Create Farm (if provided)
            farm = None
            if data.get('farm'):
                farm = CompleteFarmerRegistrationService._create_farm(
                    data['farm'], farmer, field_officer, plot
                )
            
            # Step 4: Create Irrigation (if provided)
            irrigation = None
            if data.get('irrigation') and farm:
                irrigation = CompleteFarmerRegistrationService._create_farm_irrigation(
                    data['irrigation'], farm, field_officer
                )
            
            # Manually sync plot to all FastAPI services after unified registration
            if plot:
                CompleteFarmerRegistrationService._sync_plot_to_fastapi_services(plot)
            
            return {
                'success': True,
                'farmer': farmer,
                'plot': plot,
                'farm': farm,
                'irrigation': irrigation,
                'message': 'Farmer registration completed successfully'
            }
            
        except Exception as e:
            logger.error(f"Farmer registration failed: {str(e)}")
            raise serializers.ValidationError(f"Registration failed: {str(e)}")
    
    @staticmethod
    def _create_farmer(farmer_data, field_officer=None):
        """Create farmer user"""
        if not farmer_data:
            raise serializers.ValidationError("Farmer data is required")
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not farmer_data.get(field):
                raise serializers.ValidationError(f"Farmer {field} is required")
        
        # Check if username already exists
        if User.objects.filter(username=farmer_data['username']).exists():
            raise serializers.ValidationError(f"Username '{farmer_data['username']}' already exists")
        
        # Check if email already exists
        if User.objects.filter(email=farmer_data['email']).exists():
            raise serializers.ValidationError(f"Email '{farmer_data['email']}' already exists")
        
        # Get farmer role
        try:
            from users.models import Role
            farmer_role = Role.objects.get(name='farmer')
        except Role.DoesNotExist:
            raise serializers.ValidationError("Farmer role not found in system")
        
        # Create farmer
        farmer = User.objects.create_user(
            username=farmer_data['username'],
            email=farmer_data['email'],
            password=farmer_data['password'],
            first_name=farmer_data['first_name'],
            last_name=farmer_data['last_name'],
            phone_number=farmer_data.get('phone_number', ''),
            address=farmer_data.get('address', ''),
            village=farmer_data.get('village', ''),
            state=farmer_data.get('state', ''),
            district=farmer_data.get('district', ''),
            taluka=farmer_data.get('taluka', ''),
            role=farmer_role,
            created_by=field_officer  # Set the field officer as creator
        )
        
        logger.info(f"Created farmer: {farmer.username} (ID: {farmer.id}) by {field_officer.email if field_officer else 'system'}")
        return farmer
    
    @staticmethod
    def _create_plot(plot_data, farmer, field_officer):
        """Create plot and assign to farmer"""
        if not plot_data:
            return None
        
        # Validate required fields
        required_fields = ['gat_number', 'village', 'district', 'state']
        for field in required_fields:
            if not plot_data.get(field):
                raise serializers.ValidationError(f"Plot {field} is required")
        
        # Check for duplicate plot
        existing_plot = Plot.objects.filter(
            gat_number=plot_data['gat_number'],
            plot_number=plot_data.get('plot_number', ''),
            village=plot_data['village'],
            district=plot_data['district']
        ).first()
        
        if existing_plot:
            raise serializers.ValidationError(
                f"Plot GAT {plot_data['gat_number']} in {plot_data['village']} already exists"
            )
        
        # Create plot (skip FastAPI sync during unified registration)
        plot = Plot(
            gat_number=plot_data['gat_number'],
            plot_number=plot_data.get('plot_number', ''),
            village=plot_data['village'],
            taluka=plot_data.get('taluka', ''),
            district=plot_data['district'],
            state=plot_data['state'],
            country=plot_data.get('country', 'India'),
            pin_code=plot_data.get('pin_code', ''),
            farmer=farmer,  # Auto-assign to farmer
            created_by=field_officer
        )
        
        # Skip FastAPI sync during unified registration
        plot._skip_fastapi_sync = True
        
        # Handle geometry if provided
        if plot_data.get('location'):
            plot.location = CompleteFarmerRegistrationService._convert_geojson_to_geometry(
                plot_data['location']
            )
        
        if plot_data.get('boundary'):
            plot.boundary = CompleteFarmerRegistrationService._convert_geojson_to_geometry(
                plot_data['boundary']
            )
        
        plot.save()
        
        logger.info(f"Created plot: GAT {plot.gat_number} (ID: {plot.id}) for farmer {farmer.username}")
        return plot
    
    @staticmethod
    def _create_farm(farm_data, farmer, field_officer, plot=None):
        """Create farm and assign to farmer"""
        if not farm_data:
            return None
        
        # Validate required fields
        if not farm_data.get('address'):
            raise serializers.ValidationError("Farm address is required")
        
        if not farm_data.get('area_size'):
            raise serializers.ValidationError("Farm area_size is required")
        
        # Get soil type if provided
        soil_type = None
        if farm_data.get('soil_type_id'):
            try:
                soil_type = SoilType.objects.get(id=farm_data['soil_type_id'])
            except SoilType.DoesNotExist:
                raise serializers.ValidationError(f"Soil type ID {farm_data['soil_type_id']} not found")
        elif farm_data.get('soil_type_name'):
            soil_type, _ = SoilType.objects.get_or_create(
                name=farm_data['soil_type_name'],
                defaults={'description': f"Auto-created: {farm_data['soil_type_name']}"}
            )
        
        # Get crop type if provided
        crop_type = None
        if farm_data.get('crop_type_id'):
            try:
                crop_type = CropType.objects.get(id=farm_data['crop_type_id'])
            except CropType.DoesNotExist:
                raise serializers.ValidationError(f"Crop type ID {farm_data['crop_type_id']} not found")
        elif farm_data.get('crop_type_name'):
            crop_type, _ = CropType.objects.get_or_create(
                crop_type=farm_data['crop_type_name'],
                defaults={
                    'plantation_type': farm_data.get('plantation_type', 'other'),
                    'planting_method': farm_data.get('planting_method', 'other')
                }
            )
        
        # Create farm
        farm = Farm.objects.create(
            address=farm_data['address'],
            area_size=farm_data['area_size'],
            farm_owner=farmer,  # Auto-assign to farmer
            created_by=field_officer,
            plot=plot,
            soil_type=soil_type,
            crop_type=crop_type,
            plantation_date=farm_data.get('plantation_date'),
            spacing_a=farm_data.get('spacing_a'),
            spacing_b=farm_data.get('spacing_b')
        )
        
        logger.info(f"Created farm: {farm.farm_uid} (ID: {farm.id}) for farmer {farmer.username}")
        return farm
    
    @staticmethod
    def _create_farm_irrigation(irrigation_data, farm, field_officer):
        """Create farm irrigation system"""
        if not irrigation_data:
            return None
        
        from .models import FarmIrrigation
        
        # Get irrigation type
        irrigation_type = None
        if irrigation_data.get('irrigation_type_id'):
            try:
                irrigation_type = IrrigationType.objects.get(id=irrigation_data['irrigation_type_id'])
            except IrrigationType.DoesNotExist:
                raise serializers.ValidationError(f"Irrigation type ID {irrigation_data['irrigation_type_id']} not found")
        elif irrigation_data.get('irrigation_type_name'):
            irrigation_type, _ = IrrigationType.objects.get_or_create(
                name=irrigation_data['irrigation_type_name'],
                defaults={'description': f"Auto-created: {irrigation_data['irrigation_type_name']}"}
            )
        
        # Create irrigation with location (use farm plot location as default)
        irrigation_location = None
        if irrigation_data.get('location'):
            irrigation_location = CompleteFarmerRegistrationService._convert_geojson_to_geometry(
                irrigation_data['location']
            )
        elif farm.plot and farm.plot.location:
            # Use plot location as default for irrigation
            irrigation_location = farm.plot.location
        else:
            # Default location (center of farm area or a generic point)
            from django.contrib.gis.geos import Point
            irrigation_location = Point(0, 0)  # Default to 0,0 if no location available
        
        irrigation = FarmIrrigation.objects.create(
            farm=farm,
            irrigation_type=irrigation_type,
            location=irrigation_location,
            status=irrigation_data.get('status', True),
            # Irrigation-specific fields
            motor_horsepower=irrigation_data.get('motor_horsepower'),
            pipe_width_inches=irrigation_data.get('pipe_width_inches'),
            distance_motor_to_plot_m=irrigation_data.get('distance_motor_to_plot_m'),
            plants_per_acre=irrigation_data.get('plants_per_acre'),
            flow_rate_lph=irrigation_data.get('flow_rate_lph'),
            emitters_count=irrigation_data.get('emitters_count')
        )
        
        logger.info(f"Created irrigation: {irrigation.id} for farm {farm.farm_uid}")
        return irrigation
    
    @staticmethod
    def get_registration_summary(farmer, plot, farm, irrigation):
        """Get a summary of the complete registration"""
        from users.serializers import UserSerializer
        from .serializers import PlotSerializer, FarmSerializer, FarmIrrigationSerializer
        
        summary = {
            'farmer': UserSerializer(farmer).data if farmer else None,
            'plot': PlotSerializer(plot).data if plot else None,
            'farm': FarmSerializer(farm).data if farm else None,
            'irrigation': FarmIrrigationSerializer(irrigation).data if irrigation else None,
        }
        
        return summary
    
    @staticmethod
    def _convert_geojson_to_geometry(geojson_data):
        """
        Convert GeoJSON dictionary to Django GIS geometry object
        
        Args:
            geojson_data: Dictionary with GeoJSON format
            
        Returns:
            Django GIS geometry object
        """
        try:
            from django.contrib.gis.geos import GEOSGeometry
            import json
            
            if isinstance(geojson_data, dict):
                # Validate basic GeoJSON structure
                if 'type' not in geojson_data:
                    raise ValueError("GeoJSON must have 'type' field")
                if 'coordinates' not in geojson_data:
                    raise ValueError("GeoJSON must have 'coordinates' field")
                
                # Convert dict to JSON string, then to geometry
                geojson_string = json.dumps(geojson_data)
                return GEOSGeometry(geojson_string)
            elif isinstance(geojson_data, str):
                # Already a JSON string
                return GEOSGeometry(geojson_data)
            else:
                raise ValueError(f"Invalid geometry data type: {type(geojson_data)}")
                
        except Exception as e:
            logger.error(f"Error converting GeoJSON to geometry: {str(e)}")
            raise serializers.ValidationError(f"Invalid geometry data: {str(e)}")
    
    @staticmethod
    def _sync_plot_to_fastapi_services(plot):
        """
        Manually sync a plot to all FastAPI services after unified registration
        
        Args:
            plot: Plot instance to sync
        """
        logger.info(f"Starting manual sync of plot {plot.id} to all FastAPI services")
        
        # List of all sync services
        sync_services = [
            ('events.py', 'services', 'EventsSyncService', 'sync_plot_to_events'),
            ('soil.py/main.py', 'soil_services', 'SoilSyncService', 'sync_plot_to_soil'),
            ('Admin.py', 'admin_services', 'AdminSyncService', 'sync_plot_to_admin'),
            ('ET.py', 'et_services', 'ETSyncService', 'sync_plot_to_et'),
            ('field.py', 'field_services', 'FieldSyncService', 'sync_plot_to_field'),
        ]
        
        sync_results = {
            'successful': [],
            'failed': []
        }
        
        for service_name, module_name, class_name, method_name in sync_services:
            try:
                # Dynamically import and call the sync service
                module = __import__(f'farms.{module_name}', fromlist=[class_name])
                service_class = getattr(module, class_name)
                service_instance = service_class()
                sync_method = getattr(service_instance, method_name)
                
                # Call the sync method
                result = sync_method(plot)
                
                if result:
                    sync_results['successful'].append(service_name)
                    logger.info(f"✅ Successfully synced plot {plot.id} to {service_name}")
                else:
                    sync_results['failed'].append(f"{service_name} (returned False)")
                    logger.warning(f"⚠️ Sync to {service_name} returned False for plot {plot.id}")
                    
            except Exception as e:
                sync_results['failed'].append(f"{service_name} ({str(e)})")
                logger.error(f"❌ Failed to sync plot {plot.id} to {service_name}: {str(e)}")
        
        # Log summary
        logger.info(f"Plot {plot.id} sync summary: {len(sync_results['successful'])} successful, {len(sync_results['failed'])} failed")
        
        if sync_results['successful']:
            logger.info(f"✅ Successful syncs: {', '.join(sync_results['successful'])}")
        
        if sync_results['failed']:
            logger.warning(f"❌ Failed syncs: {', '.join(sync_results['failed'])}")
        
        return sync_results
