from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import InventoryItem, InventoryTransaction
from .serializers import (
    InventoryItemSerializer, 
    InventoryItemDetailSerializer,
    InventoryTransactionSerializer
)
from django.db.models import Q
from django.utils import timezone

class IsAdminOrManager(permissions.BasePermission):
    """
    Custom permission to only allow admin and manager users to perform certain actions.
    """
    def has_permission(self, request, view):
        return request.user and (
            request.user.is_superuser or 
            request.user.role in ['admin', 'manager']
        )

class InventoryItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing inventory items.
    """
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    filterset_fields = ['category', 'status']
    search_fields = ['item_name', 'description']
    ordering_fields = ['item_name', 'quantity', 'created_at', 'updated_at']
    ordering = ['item_name']
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminOrManager()]
        return [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InventoryItemDetailSerializer
        return InventoryItemSerializer
    
    def get_queryset(self):
        queryset = InventoryItem.objects.all()
        
        # Apply filters from query parameters
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Additional filter for expired items
        show_expired = self.request.query_params.get('show_expired', 'false').lower() == 'true'
        if not show_expired:
            queryset = queryset.exclude(status='expired')
        
        # Search parameter
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(item_name__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def add_transaction(self, request, pk=None):
        """
        Add a transaction for this inventory item.
        """
        inventory_item = self.get_object()
        
        # Create serializer with the inventory item set to the current object
        data = request.data.copy()
        data['inventory_item'] = inventory_item.id
        
        serializer = InventoryTransactionSerializer(
            data=data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            # Get the updated inventory item serializer
            item_serializer = self.get_serializer_class()(
                inventory_item,
                context={'request': request}
            )
            return Response(item_serializer.data)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """
        Retrieve inventory items that are low in stock or out of stock.
        """
        queryset = self.get_queryset().filter(
            Q(status='low_stock') | Q(status='out_of_stock')
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """
        Retrieve inventory items that are expiring within 30 days.
        """
        today = timezone.now().date()
        thirty_days_later = today + timezone.timedelta(days=30)
        
        queryset = self.get_queryset().filter(
            expiry_date__isnull=False,
            expiry_date__gte=today,
            expiry_date__lte=thirty_days_later
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class InventoryTransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing inventory transactions.
    """
    queryset = InventoryTransaction.objects.all()
    serializer_class = InventoryTransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrManager]
    filterset_fields = ['inventory_item', 'transaction_type']
    ordering_fields = ['transaction_date']
    ordering = ['-transaction_date']
    
    def get_queryset(self):
        queryset = InventoryTransaction.objects.all()
        
        # Filter by inventory item
        inventory_item_id = self.request.query_params.get('inventory_item')
        if inventory_item_id:
            queryset = queryset.filter(inventory_item_id=inventory_item_id)
        
        # Filter by transaction type
        transaction_type = self.request.query_params.get('transaction_type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(transaction_date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(transaction_date__lte=end_date)
        
        return queryset
