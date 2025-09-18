from django.contrib import admin
from .models import InventoryItem, InventoryTransaction

class InventoryTransactionInline(admin.TabularInline):
    model = InventoryTransaction
    extra = 1
    readonly_fields = ['transaction_date']

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'quantity', 'unit', 'category', 'status', 'purchase_date', 'expiry_date')
    list_filter = ('status', 'category')
    search_fields = ('item_name', 'description')
    readonly_fields = ('status', 'created_at', 'updated_at')
    inlines = [InventoryTransactionInline]
    fieldsets = (
        (None, {'fields': ('item_name', 'description', 'quantity', 'unit')}),
        ('Classification', {'fields': ('category', 'status')}),
        ('Dates', {'fields': ('purchase_date', 'expiry_date')}),
        ('Thresholds', {'fields': ('reorder_level',)}),
        ('Metadata', {'fields': ('created_by', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('inventory_item', 'transaction_type', 'quantity', 'transaction_date', 'performed_by')
    list_filter = ('transaction_type', 'transaction_date')
    search_fields = ('inventory_item__item_name', 'notes')
    readonly_fields = ('transaction_date',)
    date_hierarchy = 'transaction_date'
