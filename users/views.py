from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random
import string
from .models import Role
from .serializers import (
    UserSerializer, 
    UserCreateSerializer,
    FieldOfficerWithFarmersSerializer,
    FieldOfficerSerializer,
    OwnerHierarchySerializer,
    ManagerHierarchySerializer
)
from .permissions import IsManager, IsOwner

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Enhanced create method to handle owner creation by managers.
        This creates a special relationship where:
        - Manager creates the owner
        - Owner can monitor the manager who created them
        - Owner gets elevated permissions to view all managers
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if creating an owner
        role_id = serializer.validated_data.get('role_id')
        if role_id == 4:  # Owner role
            # Special logic for owner creation
            owner_data = serializer.validated_data.copy()
            owner_data['created_by'] = request.user  # Manager who creates owner
            
            # Create the owner
            owner = User.objects.create_user(**owner_data)
            
            # Return special response for owner creation
            return Response({
                'success': True,
                'message': 'Owner created successfully. Owner can now monitor all managers including the one who created them.',
                'id': owner.id,
                'username': owner.username,
                'email': owner.email,
                'role': {
                    'id': owner.role.id,
                    'name': owner.role.name,
                    'display_name': owner.role.display_name
                },
                'created_by': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'role': request.user.role.name if request.user.role else 'unknown'
                },
                'note': 'Owner has elevated permissions to monitor all managers'
            }, status=201)
        else:
            # Normal user creation
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=201, headers=headers)
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsManager()]
        elif self.action == 'my_field_officers':
            return [permissions.IsAuthenticated()] # Logic is handled inside the view
        elif self.action == 'owner_hierarchy':
            return [IsOwner()]
        elif self.action in ['send_otp', 'verify_otp']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        # Super Admin can see all users
        if user.is_superuser or user.has_role('admin'):
            return User.objects.all()
        # Manager sees agronomists, quality control, field officers, farmers
        if user.has_role('manager'):
            return User.objects.filter(role__name__in=['agronomist', 'qualitycontrol', 'fieldofficer', 'farmer'])
        # Owner can see all managers (including the one who created them) and their hierarchy
        if user.has_role('owner'):
            # Special case: Owner can monitor all managers and their subordinates
            return User.objects.filter(
                role__name__in=['manager', 'fieldofficer', 'farmer']
            )
        # Default: only own record
        return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'], url_path='my-field-officers')
    def my_field_officers(self, request):
        """
        Get field officers.
        - If logged in as a Manager, returns field officers created by that manager.
        - If logged in as an Owner, returns all managers and their field officers.
        """
        user = request.user

        if user.has_role('manager'):
            # Manager's view: their own field officers
            field_officers = user.created_users.filter(role__name='fieldofficer')
            
            total_farmers = 0
            total_plots = 0
            for fo in field_officers:
                farmers_under_fo = fo.created_users.filter(role__name='farmer')
                total_farmers += farmers_under_fo.count()
                for farmer in farmers_under_fo:
                    total_plots += farmer.plots.count()

            serializer = FieldOfficerWithFarmersSerializer(field_officers, many=True, context={'request': request})
            
            return Response({
                "manager": {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                "summary": {
                    "total_field_officers": field_officers.count(),
                    "total_farmers": total_farmers,
                    "total_plots": total_plots,
                },
                "field_officers": serializer.data
            })

        elif user.has_role('owner'):
            # Owner's view: all managers and their hierarchies
            managers = User.objects.filter(role__name='manager')
            serializer = ManagerHierarchySerializer(managers, many=True)
            return Response({
                "owner_view": True,
                "managers": serializer.data
            })

        else:
            return Response({"error": "You do not have permission to access this endpoint."}, status=status.HTTP_403_FORBIDDEN)
    
    
    @action(detail=False, methods=['get'], url_path='owner-hierarchy')
    def owner_hierarchy(self, request):
        """
        Get complete hierarchy for Owner:
        - All managers (including the one who created this owner)
        - Field officers under each manager
        - Farmers under each field officer
        - Total counts and statistics
        """
        # Get the current owner user
        owner = request.user
        
        # Serialize the owner with complete hierarchy
        serializer = OwnerHierarchySerializer(owner)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='my-creator')
    def my_creator(self, request):
        """
        Special endpoint for owners to see who created them (the manager).
        This handles the special case where managers create owners.
        """
        user = request.user
        
        if user.has_role('owner') and user.created_by:
            # Owner can see the manager who created them
            creator = user.created_by
            return Response({
                'success': True,
                'creator': {
                    'id': creator.id,
                    'username': creator.username,
                    'email': creator.email,
                    'role': creator.role.name if creator.role else 'unknown',
                    'first_name': creator.first_name,
                    'last_name': creator.last_name,
                    'note': 'This manager created you as an owner. You can now monitor them and all other managers.'
                }
            })
        elif user.has_role('owner'):
            return Response({
                'success': True,
                'creator': None,
                'note': 'You are a system owner with no specific creator. You can monitor all managers.'
            })
        else:
            return Response({
                'error': 'Only owners can access this endpoint'
            }, status=403)
    
    @action(detail=False, methods=['get'], url_path='contact-details')
    def contact_details(self, request):
        """
        Get contact details based on user role and hierarchy position.
        
        - Manager: Shows owner, field officers, and farmers contact details
        - Field Officer: Shows manager, owner, and farmers contact details  
        - Farmer: Shows field officer, manager, and owner contact details
        """
        user = request.user
        
        if user.has_role('manager'):
            return self._get_manager_contacts(user)
        elif user.has_role('fieldofficer'):
            return self._get_field_officer_contacts(user)
        elif user.has_role('farmer'):
            return self._get_farmer_contacts(user)
        elif user.has_role('owner'):
            return self._get_owner_contacts(user)
        else:
            return Response({
                'error': 'Invalid user role for contact details'
            }, status=403)
    
    def _get_manager_contacts(self, manager):
        """Get contact details for manager"""
        # Get owner (if manager was created by owner, or any owner in system)
        owners = User.objects.filter(role__name='owner')
        owner_contact = None
        if owners.exists():
            owner = owners.first()
            owner_contact = {
                'id': owner.id,
                'name': f"{owner.first_name} {owner.last_name}".strip() or owner.username,
                'role': 'Owner',
                'email': owner.email,
                'phone': owner.phone_number,
                'address': f"{owner.address}, {owner.village}, {owner.district}, {owner.state}".replace(', , ', ', ').strip(', ')
            }
        
        # Get field officers created by this manager
        field_officers = manager.created_users.filter(role__name='fieldofficer')
        field_officer_contacts = []
        for fo in field_officers:
            field_officer_contacts.append({
                'id': fo.id,
                'name': f"{fo.first_name} {fo.last_name}".strip() or fo.username,
                'role': 'Field Officer',
                'email': fo.email,
                'phone': fo.phone_number,
                'address': f"{fo.address}, {fo.village}, {fo.district}, {fo.state}".replace(', , ', ', ').strip(', '),
                'farmers_count': fo.created_users.filter(role__name='farmer').count()
            })
        
        # Get farmers created by field officers under this manager
        farmers = User.objects.filter(
            role__name='farmer',
            created_by__in=field_officers
        )
        farmer_contacts = []
        for farmer in farmers:
            farmer_contacts.append({
                'id': farmer.id,
                'name': f"{farmer.first_name} {farmer.last_name}".strip() or farmer.username,
                'role': 'Farmer',
                'email': farmer.email,
                'phone': farmer.phone_number,
                'address': f"{farmer.address}, {farmer.village}, {farmer.district}, {farmer.state}".replace(', , ', ', ').strip(', '),
                'field_officer': farmer.created_by.username if farmer.created_by else None
            })
        
        return Response({
            'user_role': 'Manager',
            'user_name': f"{manager.first_name} {manager.last_name}".strip() or manager.username,
            'contacts': {
                'owner': owner_contact,
                'field_officers': field_officer_contacts,
                'farmers': farmer_contacts
            },
            'summary': {
                'total_field_officers': len(field_officer_contacts),
                'total_farmers': len(farmer_contacts)
            }
        })
    
    def _get_field_officer_contacts(self, field_officer):
        """Get contact details for field officer"""
        # Get manager who created this field officer
        manager_contact = None
        if field_officer.created_by and field_officer.created_by.has_role('manager'):
            manager = field_officer.created_by
            manager_contact = {
                'id': manager.id,
                'name': f"{manager.first_name} {manager.last_name}".strip() or manager.username,
                'role': 'Manager',
                'email': manager.email,
                'phone': manager.phone_number,
                'address': f"{manager.address}, {manager.village}, {manager.district}, {manager.state}".replace(', , ', ', ').strip(', ')
            }
        
        # Get owner (any owner in system)
        owners = User.objects.filter(role__name='owner')
        owner_contact = None
        if owners.exists():
            owner = owners.first()
            owner_contact = {
                'id': owner.id,
                'name': f"{owner.first_name} {owner.last_name}".strip() or owner.username,
                'role': 'Owner',
                'email': owner.email,
                'phone': owner.phone_number,
                'address': f"{owner.address}, {owner.village}, {owner.district}, {owner.state}".replace(', , ', ', ').strip(', ')
            }
        
        # Get farmers created by this field officer
        farmers = field_officer.created_users.filter(role__name='farmer')
        farmer_contacts = []
        for farmer in farmers:
            farmer_contacts.append({
                'id': farmer.id,
                'name': f"{farmer.first_name} {farmer.last_name}".strip() or farmer.username,
                'role': 'Farmer',
                'email': farmer.email,
                'phone': farmer.phone_number,
                'address': f"{farmer.address}, {farmer.village}, {farmer.district}, {farmer.state}".replace(', , ', ', ').strip(', ')
            })
        
        return Response({
            'user_role': 'Field Officer',
            'user_name': f"{field_officer.first_name} {field_officer.last_name}".strip() or field_officer.username,
            'contacts': {
                'manager': manager_contact,
                'owner': owner_contact,
                'farmers': farmer_contacts
            },
            'summary': {
                'total_farmers': len(farmer_contacts)
            }
        })
    
    def _get_farmer_contacts(self, farmer):
        """Get contact details for farmer"""
        # Get field officer who created this farmer
        field_officer_contact = None
        if farmer.created_by and farmer.created_by.has_role('fieldofficer'):
            fo = farmer.created_by
            field_officer_contact = {
                'id': fo.id,
                'name': f"{fo.first_name} {fo.last_name}".strip() or fo.username,
                'role': 'Field Officer',
                'email': fo.email,
                'phone': fo.phone_number,
                'address': f"{fo.address}, {fo.village}, {fo.district}, {fo.state}".replace(', , ', ', ').strip(', ')
            }
        
        # Get manager (through field officer)
        manager_contact = None
        if farmer.created_by and farmer.created_by.created_by and farmer.created_by.created_by.has_role('manager'):
            manager = farmer.created_by.created_by
            manager_contact = {
                'id': manager.id,
                'name': f"{manager.first_name} {manager.last_name}".strip() or manager.username,
                'role': 'Manager',
                'email': manager.email,
                'phone': manager.phone_number,
                'address': f"{manager.address}, {manager.village}, {manager.district}, {manager.state}".replace(', , ', ', ').strip(', ')
            }
        
        # Get owner (any owner in system)
        owners = User.objects.filter(role__name='owner')
        owner_contact = None
        if owners.exists():
            owner = owners.first()
            owner_contact = {
                'id': owner.id,
                'name': f"{owner.first_name} {owner.last_name}".strip() or owner.username,
                'role': 'Owner',
                'email': owner.email,
                'phone': owner.phone_number,
                'address': f"{owner.address}, {owner.village}, {owner.district}, {owner.state}".replace(', , ', ', ').strip(', ')
            }
        
        return Response({
            'user_role': 'Farmer',
            'user_name': f"{farmer.first_name} {farmer.last_name}".strip() or farmer.username,
            'contacts': {
                'field_officer': field_officer_contact,
                'manager': manager_contact,
                'owner': owner_contact
            }
        })
    
    def _get_owner_contacts(self, owner):
        """Get contact details for owner"""
        # Get all managers
        managers = User.objects.filter(role__name='manager')
        manager_contacts = []
        for manager in managers:
            manager_contacts.append({
                'id': manager.id,
                'name': f"{manager.first_name} {manager.last_name}".strip() or manager.username,
                'role': 'Manager',
                'email': manager.email,
                'phone': manager.phone_number,
                'address': f"{manager.address}, {manager.village}, {manager.district}, {manager.state}".replace(', , ', ', ').strip(', '),
                'field_officers_count': manager.created_users.filter(role__name='fieldofficer').count()
            })
        
        # Get all field officers
        field_officers = User.objects.filter(role__name='fieldofficer')
        field_officer_contacts = []
        for fo in field_officers:
            field_officer_contacts.append({
                'id': fo.id,
                'name': f"{fo.first_name} {fo.last_name}".strip() or fo.username,
                'role': 'Field Officer',
                'email': fo.email,
                'phone': fo.phone_number,
                'address': f"{fo.address}, {fo.village}, {fo.district}, {fo.state}".replace(', , ', ', ').strip(', '),
                'manager': fo.created_by.username if fo.created_by else None,
                'farmers_count': fo.created_users.filter(role__name='farmer').count()
            })
        
        # Get all farmers
        farmers = User.objects.filter(role__name='farmer')
        farmer_contacts = []
        for farmer in farmers:
            farmer_contacts.append({
                'id': farmer.id,
                'name': f"{farmer.first_name} {farmer.last_name}".strip() or farmer.username,
                'role': 'Farmer',
                'email': farmer.email,
                'phone': farmer.phone_number,
                'address': f"{farmer.address}, {farmer.village}, {farmer.district}, {farmer.state}".replace(', , ', ', ').strip(', '),
                'field_officer': farmer.created_by.username if farmer.created_by else None
            })
        
        return Response({
            'user_role': 'Owner',
            'user_name': f"{owner.first_name} {owner.last_name}".strip() or owner.username,
            'contacts': {
                'managers': manager_contacts,
                'field_officers': field_officer_contacts,
                'farmers': farmer_contacts
            },
            'summary': {
                'total_managers': len(manager_contacts),
                'total_field_officers': len(field_officer_contacts),
                'total_farmers': len(farmer_contacts)
            }
        })
    
    @action(detail=False, methods=['get'], url_path='hierarchy-summary')
    def hierarchy_summary(self, request):
        """
        Get a summary of the hierarchy for any authenticated user
        """
        user = request.user
        
        if user.has_role('owner'):
            # Owner sees summary of all levels
            summary = {
                'role': 'owner',
                'total_managers': User.objects.filter(role__name='manager').count(),
                'total_field_officers': User.objects.filter(role__name='fieldofficer').count(),
                'total_farmers': User.objects.filter(role__name='farmer').count(),
                'message': 'Use /owner-hierarchy/ for complete details'
            }
        elif user.has_role('manager'):
            # Manager sees their field officers and farmers
            field_officers = user.created_users.filter(role__name='fieldofficer')
            total_farmers = 0
            for fo in field_officers:
                total_farmers += fo.created_users.filter(role__name='farmer').count()
            
            summary = {
                'role': 'manager',
                'field_officers_count': field_officers.count(),
                'total_farmers_count': total_farmers,
                'message': 'Use /my-field-officers/ for field officer details'
            }
        elif user.has_role('fieldofficer'):
            # Field officer sees their farmers
            farmers_count = user.created_users.filter(role__name='farmer').count()
            summary = {
                'role': 'fieldofficer',
                'farmers_count': farmers_count,
                'message': 'Use /my-farmers/ for farmer details'
            }
        elif user.has_role('farmer'):
            summary = {
                'role': 'farmer',
                'message': 'You are at the bottom level of the hierarchy'
            }
        else:
            summary = {
                'role': 'unknown',
                'message': 'No role assigned'
            }
        
        return Response(summary)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], url_path='login')
    def login(self, request):
        """
        Login with email and password
        """
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'detail': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Find user by email
            user = User.objects.filter(email=email).first()
            if not user:
                return Response({
                    'detail': 'Invalid email or password'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check password
            if not user.check_password(password):
                return Response({
                    'detail': 'Invalid email or password'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check if user is active
            if not user.is_active:
                return Response({
                    'detail': 'Account is deactivated'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Generate JWT tokens
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': {
                        'id': user.role.id,
                        'name': user.role.name,
                        'display_name': user.role.display_name
                    } if user.role else None
                }
            })
            
        except Exception as e:
            return Response({
                'detail': f'Login error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request, pk=None):
        user_obj = self.get_object()
        from .serializers import ChangePasswordSerializer
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not user_obj.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': 'Wrong password.'}, status=status.HTTP_400_BAD_REQUEST)

        user_obj.set_password(serializer.validated_data['new_password'])
        user_obj.save()
        return Response({'status': 'password changed'})

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user = request.user
        
        # Check if user is a farmer (role ID 1)
        if user.role and user.role.id == 1:  # farmer role
            from .serializers import FarmerDetailSerializer
            serializer = FarmerDetailSerializer(user)
        else:
            # Use default serializer for non-farmers
            serializer = self.get_serializer(user)
        
        return Response(serializer.data)
