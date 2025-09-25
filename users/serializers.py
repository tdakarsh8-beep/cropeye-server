from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Role

User = get_user_model()

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'display_name']

class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'address', 'village', 'taluka', 'district', 'state',
            'role', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class FarmerDetailSerializer(UserSerializer):
    """Enhanced serializer for farmers with irrigation and plantation details"""
    
    # Basic user info (inherited from UserSerializer)
    # role, created_by, created_at, updated_at are already included
    
    # Farmer-specific agricultural data
    plots = serializers.SerializerMethodField()
    farms = serializers.SerializerMethodField()
    irrigation_details = serializers.SerializerMethodField()
    plantation_details = serializers.SerializerMethodField()
    agricultural_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'address', 'village', 'taluka', 'district', 'state',
            'role', 'created_by', 'created_at', 'updated_at',
            'plots', 'farms', 'irrigation_details', 'plantation_details', 'agricultural_summary'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_plots(self, obj):
        """Get all plots owned by the farmer"""
        plots_data = []
        for plot in obj.plots.all():
            plot_info = {
                'id': plot.id,
                'gat_number': plot.gat_number,
                'plot_number': plot.plot_number,
                'village': plot.village,
                'taluka': plot.taluka,
                'district': plot.district,
                'state': plot.state,
                'country': plot.country,
                'pin_code': plot.pin_code,
                'location': {
                    'type': 'Point',
                    'coordinates': [plot.location.x, plot.location.y] if plot.location else None
                } if plot.location else None,
                'boundary': {
                    'type': 'Polygon',
                    'coordinates': plot.boundary.coords[0] if plot.boundary else None
                } if plot.boundary else None,
                'created_at': plot.created_at.isoformat() if plot.created_at else None,
                'updated_at': plot.updated_at.isoformat() if plot.updated_at else None
            }
            plots_data.append(plot_info)
        return plots_data
    
    def get_farms(self, obj):
        """Get all farms owned by the farmer"""
        farms_data = []
        for farm in obj.farms.all():
            farm_info = {
                'id': farm.id,
                'farm_uid': str(farm.farm_uid),
                'address': farm.address,
                'area_size': str(farm.area_size) if farm.area_size else None,
                'area_size_numeric': float(farm.area_size) if farm.area_size else None,
                'spacing_a': float(farm.spacing_a) if farm.spacing_a else None,
                'spacing_b': float(farm.spacing_b) if farm.spacing_b else None,
                'plantation_date': farm.plantation_date.isoformat() if farm.plantation_date else None,
                'plants_in_field': farm.plants_in_field,
                'soil_type': {
                    'id': farm.soil_type.id,
                    'name': farm.soil_type.name
                } if farm.soil_type else None,
                'crop_type': {
                    'id': farm.crop_type.id,
                    'crop_type': farm.crop_type.crop_type,
                    'plantation_type': farm.crop_type.plantation_type,
                    'plantation_type_display': farm.crop_type.get_plantation_type_display(),
                    'planting_method': farm.crop_type.planting_method,
                    'planting_method_display': farm.crop_type.get_planting_method_display()
                } if farm.crop_type else None,
                'farm_document': {
                    'name': farm.farm_document.name.split('/')[-1] if farm.farm_document else None,
                    'url': farm.farm_document.url if farm.farm_document else None,
                    'size': farm.farm_document.size if farm.farm_document else None
                } if farm.farm_document else None,
                'created_at': farm.created_at.isoformat() if farm.created_at else None,
                'updated_at': farm.updated_at.isoformat() if farm.updated_at else None,
                'created_by': {
                    'id': farm.created_by.id,
                    'username': farm.created_by.username,
                    'full_name': f"{farm.created_by.first_name} {farm.created_by.last_name}".strip() or farm.created_by.username,
                    'email': farm.created_by.email,
                    'phone_number': farm.created_by.phone_number
                } if farm.created_by else None
            }
            farms_data.append(farm_info)
        return farms_data
    
    def get_irrigation_details(self, obj):
        """Get all irrigation details for the farmer's farms"""
        irrigation_data = []
        for farm in obj.farms.all():
            for irrigation in farm.irrigations.all():
                irrigation_info = {
                    'id': irrigation.id,
                    'farm_id': farm.id,
                    'farm_uid': str(farm.farm_uid),
                    'irrigation_type': irrigation.irrigation_type.get_name_display() if irrigation.irrigation_type else None,
                    'irrigation_type_code': irrigation.irrigation_type.name if irrigation.irrigation_type else None,
                    'location': {
                        'type': 'Point',
                        'coordinates': [irrigation.location.x, irrigation.location.y] if irrigation.location else None
                    } if irrigation.location else None,
                    'status': irrigation.status,
                    'status_display': 'Active' if irrigation.status else 'Inactive',
                    'motor_horsepower': irrigation.motor_horsepower,
                    'pipe_width_inches': irrigation.pipe_width_inches,
                    'distance_motor_to_plot_m': irrigation.distance_motor_to_plot_m,
                    'plants_per_acre': irrigation.plants_per_acre,
                    'flow_rate_lph': irrigation.flow_rate_lph,
                    'emitters_count': irrigation.emitters_count
                }
                irrigation_data.append(irrigation_info)
        return irrigation_data
    
    def get_plantation_details(self, obj):
        """Get plantation details from crop types"""
        plantation_data = []
        for farm in obj.farms.all():
            if farm.crop_type:
                plantation_info = {
                    'farm_id': farm.id,
                    'farm_uid': str(farm.farm_uid),
                    'crop_type': farm.crop_type.crop_type,
                    'plantation_type': farm.crop_type.plantation_type,
                    'plantation_type_display': farm.crop_type.get_plantation_type_display(),
                    'planting_method': farm.crop_type.planting_method,
                    'planting_method_display': farm.crop_type.get_planting_method_display(),
                    'plantation_date': farm.plantation_date.isoformat() if farm.plantation_date else None,
                    'area_size': str(farm.area_size) if farm.area_size else None,
                    'soil_type': farm.soil_type.name if farm.soil_type else None
                }
                plantation_data.append(plantation_info)
        return plantation_data
    
    def get_agricultural_summary(self, obj):
        """Get agricultural summary statistics"""
        total_plots = obj.plots.count()
        total_farms = obj.farms.count()
        total_irrigations = sum(farm.irrigations.count() for farm in obj.farms.all())
        
        # Get unique irrigation types
        irrigation_types = set()
        for farm in obj.farms.all():
            for irrigation in farm.irrigations.all():
                if irrigation.irrigation_type:
                    irrigation_types.add(irrigation.irrigation_type.get_name_display())
        
        # Get unique crop types
        crop_types = set()
        for farm in obj.farms.all():
            if farm.crop_type and farm.crop_type.crop_type:
                crop_types.add(farm.crop_type.crop_type)
        
        # Calculate total area
        total_area = sum(float(farm.area_size) for farm in obj.farms.all() if farm.area_size)
        
        return {
            'total_plots': total_plots,
            'total_farms': total_farms,
            'total_irrigations': total_irrigations,
            'total_area_acres': round(total_area, 2),
            'irrigation_types': list(irrigation_types),
            'crop_types': list(crop_types),
            'plots_with_boundaries': obj.plots.filter(boundary__isnull=False).count(),
            'plots_with_locations': obj.plots.filter(location__isnull=False).count()
        }

class FieldOfficerSerializer(UserSerializer):
    role = RoleSerializer(read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    
    # Count of farmers, plots, and farms created by this field officer
    farmers_count = serializers.SerializerMethodField()
    plots_count = serializers.SerializerMethodField()
    farms_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'address', 'village', 'taluka', 'district', 'state',
            'role', 'created_by', 'created_at', 'updated_at',
            'farmers_count', 'plots_count', 'farms_count'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_farmers_count(self, obj):
        return obj.created_users.filter(role__name='farmer').count()
    
    def get_plots_count(self, obj):
        # This will be updated when we have the plots model
        return 0
    
    def get_farms_count(self, obj):
        # This will be updated when we have the farms model
        return 0

class FarmerSerializer(UserSerializer):
    role = RoleSerializer(read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'address', 'village', 'taluka', 'district', 'state',
            'role', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class ManagerHierarchySerializer(UserSerializer):
    """Serializer for Manager showing their field officers and farmers"""
    role = RoleSerializer(read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    
    # Field officers under this manager
    field_officers = serializers.SerializerMethodField()
    field_officers_count = serializers.SerializerMethodField()
    
    # Farmers under this manager (through field officers)
    total_farmers_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'address', 'village', 'taluka', 'district', 'state',
            'role', 'created_by', 'created_at', 'updated_at',
            'field_officers', 'field_officers_count', 'total_farmers_count'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_field_officers(self, obj):
        """Get all field officers created by this manager"""
        field_officers = obj.created_users.filter(role__name='fieldofficer')
        return FieldOfficerSerializer(field_officers, many=True).data
    
    def get_field_officers_count(self, obj):
        """Count of field officers under this manager"""
        return obj.created_users.filter(role__name='fieldofficer').count()
    
    def get_total_farmers_count(self, obj):
        """Count of total farmers under this manager (through field officers)"""
        total = 0
        for field_officer in obj.created_users.filter(role__name='fieldofficer'):
            total += field_officer.created_users.filter(role__name='farmer').count()
        return total

class OwnerHierarchySerializer(serializers.ModelSerializer):
    """Serializer for Owner showing complete hierarchy"""
    role = RoleSerializer(read_only=True)
    
    # All managers in the system
    managers = serializers.SerializerMethodField()
    managers_count = serializers.SerializerMethodField()
    
    # Total counts across all hierarchy
    total_field_officers = serializers.SerializerMethodField()
    total_farmers = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'address', 'village', 'taluka', 'district', 'state',
            'role', 'created_at', 'updated_at',
            'managers', 'managers_count', 'total_field_officers', 'total_farmers'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_managers(self, obj):
        """Get all managers in the system"""
        # Special logic: Owner can monitor all managers, including the one who created them
        managers = User.objects.filter(role__name='manager')
        return ManagerHierarchySerializer(managers, many=True).data
    
    def get_managers_count(self, obj):
        """Count of total managers"""
        return User.objects.filter(role__name='manager').count()
    
    def get_total_field_officers(self, obj):
        """Count of total field officers across all managers"""
        return User.objects.filter(role__name='fieldofficer').count()
    
    def get_total_farmers(self, obj):
        """Count of total farmers across all field officers"""
        return User.objects.filter(role__name='farmer').count()

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'phone_number', 'address', 'village', 'taluka', 'district', 'state',
            'role_id'
        ]
    
    def validate_role_id(self, value):
        """Validate that the role exists and is appropriate"""
        try:
            role = Role.objects.get(id=value)
        except Role.DoesNotExist:
            raise serializers.ValidationError("Invalid role ID.")
        
        # Check if trying to create owner (role_id = 4)
        if value == 4:  # Owner role
            # Only managers can create owners - this is handled in view permissions
            # Additional validation can be added here if needed
            pass
        
        return value
    
    def validate_email(self, value):
        """Ensure email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_username(self, value):
        """Ensure username is unique"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def create(self, validated_data):
        role_id = validated_data.pop('role_id')
        password = validated_data.pop('password')
        
        # Get the role
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise serializers.ValidationError(f"Role with ID {role_id} does not exist")
        
        # Set created_by to the current user (manager)
        user = User.objects.create_user(
            **validated_data,
            role=role,
            created_by=self.context['request'].user
        )
        user.set_password(password)
        user.save()
        
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        source='role',
        required=False
    )

    class Meta:
        model = User
        fields = [
            'email','first_name', 'last_name', 'role_id', 'phone_number', 'address',
            'village', 'state', 'district', 'taluka', 'profile_picture',
        ]
        read_only_fields = ['email']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords must match.")
        return data
