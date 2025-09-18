from rest_framework import serializers
from .models import Vendor, PurchaseOrder, PurchaseOrderItem, VendorCommunication
from inventory.serializers import InventoryItemSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class VendorSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Vendor
        fields = [
            'id', 'vendor_name', 'contact_person', 'email', 'phone', 
            'address', 'website', 'rating', 'notes', 
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def create(self, validated_data):
        # Set the created_by field to the current user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    inventory_item_name = serializers.CharField(source='inventory_item.item_name', read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id', 'purchase_order', 'inventory_item', 'inventory_item_name',
            'quantity', 'unit_price', 'total_price', 'notes'
        ]

class PurchaseOrderSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    vendor_name = serializers.CharField(source='vendor.vendor_name', read_only=True)
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'vendor', 'vendor_name', 'order_number', 'status',
            'created_by', 'approved_by', 'issue_date', 'expected_delivery_date',
            'delivery_date', 'notes', 'total_amount', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['total_amount', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Set the created_by field to the current user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class VendorCommunicationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    vendor_name = serializers.CharField(source='vendor.vendor_name', read_only=True)
    purchase_order_number = serializers.CharField(source='purchase_order.order_number', read_only=True)
    
    class Meta:
        model = VendorCommunication
        fields = [
            'id', 'vendor', 'vendor_name', 'purchase_order', 'purchase_order_number',
            'communication_type', 'subject', 'message', 'date',
            'user', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def create(self, validated_data):
        # Set the user field to the current user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class VendorDetailSerializer(VendorSerializer):
    purchase_orders = PurchaseOrderSerializer(many=True, read_only=True)
    communications = VendorCommunicationSerializer(many=True, read_only=True)
    
    class Meta(VendorSerializer.Meta):
        fields = VendorSerializer.Meta.fields + ['purchase_orders', 'communications']

class PurchaseOrderDetailSerializer(PurchaseOrderSerializer):
    communications = VendorCommunicationSerializer(many=True, read_only=True)
    
    class Meta(PurchaseOrderSerializer.Meta):
        fields = PurchaseOrderSerializer.Meta.fields + ['communications'] 