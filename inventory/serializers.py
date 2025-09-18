from rest_framework import serializers
from .models import InventoryItem, InventoryTransaction
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class InventoryItemSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    status = serializers.CharField(read_only=True)
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'item_name', 'description', 'quantity', 'unit', 
            'purchase_date', 'expiry_date', 'category', 'status', 
            'reorder_level', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user
        return super().create(validated_data)

class InventoryTransactionSerializer(serializers.ModelSerializer):
    performed_by = UserSerializer(read_only=True)
    inventory_item_name = serializers.CharField(source='inventory_item.item_name', read_only=True)
    
    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'inventory_item', 'inventory_item_name', 'transaction_type', 
            'quantity', 'transaction_date', 'performed_by', 'notes'
        ]
        read_only_fields = ['transaction_date']
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['performed_by'] = user
        return super().create(validated_data)

class InventoryItemDetailSerializer(InventoryItemSerializer):
    transactions = InventoryTransactionSerializer(many=True, read_only=True)
    
    class Meta(InventoryItemSerializer.Meta):
        fields = InventoryItemSerializer.Meta.fields + ['transactions'] 