from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Vendor, PurchaseOrder, PurchaseOrderItem, VendorCommunication
from .serializers import (
    VendorSerializer, 
    VendorDetailSerializer,
    PurchaseOrderSerializer, 
    PurchaseOrderDetailSerializer,
    PurchaseOrderItemSerializer,
    VendorCommunicationSerializer
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

class VendorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing vendors.
    """
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    filterset_fields = ['rating']
    search_fields = ['vendor_name', 'contact_person', 'email', 'phone']
    ordering_fields = ['vendor_name', 'rating', 'created_at']
    ordering = ['vendor_name']
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminOrManager()]
        return [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return VendorDetailSerializer
        return VendorSerializer
    
    def get_queryset(self):
        queryset = Vendor.objects.all()
        
        # Search parameter
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(vendor_name__icontains=search) | 
                Q(contact_person__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        
        # Rating filter
        rating = self.request.query_params.get('rating')
        if rating:
            queryset = queryset.filter(rating=rating)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def add_communication(self, request, pk=None):
        """
        Add a communication record for this vendor.
        """
        vendor = self.get_object()
        
        # Create serializer with the vendor set to the current object
        data = request.data.copy()
        data['vendor'] = vendor.id
        
        serializer = VendorCommunicationSerializer(
            data=data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            # Get the updated vendor serializer
            vendor_serializer = VendorDetailSerializer(
                vendor,
                context={'request': request}
            )
            return Response(vendor_serializer.data)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing purchase orders.
    """
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    filterset_fields = ['vendor', 'status']
    search_fields = ['order_number', 'notes']
    ordering_fields = ['issue_date', 'expected_delivery_date', 'total_amount']
    ordering = ['-issue_date']
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminOrManager()]
        return [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PurchaseOrderDetailSerializer
        return PurchaseOrderSerializer
    
    def get_queryset(self):
        queryset = PurchaseOrder.objects.all()
        
        # Filter by vendor
        vendor_id = self.request.query_params.get('vendor')
        if vendor_id:
            queryset = queryset.filter(vendor_id=vendor_id)
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(issue_date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(issue_date__lte=end_date)
        
        # Search parameter
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) | 
                Q(notes__icontains=search)
            )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        """
        Add an item to this purchase order.
        """
        purchase_order = self.get_object()
        
        # Create serializer with the purchase order set to the current object
        data = request.data.copy()
        data['purchase_order'] = purchase_order.id
        
        serializer = PurchaseOrderItemSerializer(
            data=data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            # Get the updated purchase order serializer
            po_serializer = PurchaseOrderDetailSerializer(
                purchase_order,
                context={'request': request}
            )
            return Response(po_serializer.data)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve the purchase order.
        """
        purchase_order = self.get_object()
        
        if purchase_order.status != 'sent':
            return Response(
                {'detail': 'Only orders with status "sent" can be approved.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the purchase order status
        purchase_order.status = 'approved'
        purchase_order.approved_by = request.user
        purchase_order.save()
        
        serializer = PurchaseOrderDetailSerializer(
            purchase_order,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """
        Mark the purchase order as received.
        """
        purchase_order = self.get_object()
        
        if purchase_order.status != 'approved':
            return Response(
                {'detail': 'Only orders with status "approved" can be marked as received.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the purchase order status
        purchase_order.status = 'received'
        purchase_order.delivery_date = timezone.now().date()
        purchase_order.save()
        
        serializer = PurchaseOrderDetailSerializer(
            purchase_order,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel the purchase order.
        """
        purchase_order = self.get_object()
        
        if purchase_order.status == 'received':
            return Response(
                {'detail': 'Cannot cancel a received order.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the purchase order status
        purchase_order.status = 'cancelled'
        purchase_order.save()
        
        serializer = PurchaseOrderDetailSerializer(
            purchase_order,
            context={'request': request}
        )
        return Response(serializer.data)

class PurchaseOrderItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing purchase order items.
    """
    queryset = PurchaseOrderItem.objects.all()
    serializer_class = PurchaseOrderItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrManager]
    filterset_fields = ['purchase_order', 'inventory_item']
    
    def get_queryset(self):
        queryset = PurchaseOrderItem.objects.all()
        
        # Filter by purchase order
        po_id = self.request.query_params.get('purchase_order')
        if po_id:
            queryset = queryset.filter(purchase_order_id=po_id)
        
        # Filter by inventory item
        item_id = self.request.query_params.get('inventory_item')
        if item_id:
            queryset = queryset.filter(inventory_item_id=item_id)
        
        return queryset

class VendorCommunicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing vendor communications.
    """
    queryset = VendorCommunication.objects.all()
    serializer_class = VendorCommunicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['vendor', 'purchase_order', 'communication_type']
    search_fields = ['subject', 'message']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']
    
    def get_queryset(self):
        queryset = VendorCommunication.objects.all()
        
        # Filter by vendor
        vendor_id = self.request.query_params.get('vendor')
        if vendor_id:
            queryset = queryset.filter(vendor_id=vendor_id)
        
        # Filter by purchase order
        po_id = self.request.query_params.get('purchase_order')
        if po_id:
            queryset = queryset.filter(purchase_order_id=po_id)
        
        # Filter by communication type
        comm_type = self.request.query_params.get('communication_type')
        if comm_type:
            queryset = queryset.filter(communication_type=comm_type)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Search parameter
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(subject__icontains=search) | 
                Q(message__icontains=search)
            )
        
        return queryset
