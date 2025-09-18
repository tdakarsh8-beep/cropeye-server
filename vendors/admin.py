from django.contrib import admin
from .models import Vendor, PurchaseOrder, PurchaseOrderItem, VendorCommunication

class PurchaseOrderInline(admin.TabularInline):
    model = PurchaseOrder
    extra = 0
    fields = ['order_number', 'status', 'issue_date', 'expected_delivery_date', 'total_amount']
    readonly_fields = ['total_amount']
    show_change_link = True

class VendorCommunicationInline(admin.TabularInline):
    model = VendorCommunication
    extra = 0
    fields = ['communication_type', 'subject', 'date', 'user']
    readonly_fields = ['date', 'user']
    show_change_link = True

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('vendor_name', 'contact_person', 'email', 'phone', 'rating')
    list_filter = ('rating',)
    search_fields = ('vendor_name', 'contact_person', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PurchaseOrderInline, VendorCommunicationInline]
    fieldsets = (
        (None, {'fields': ('vendor_name', 'contact_person', 'email', 'phone')}),
        ('Additional Information', {'fields': ('address', 'website', 'rating', 'notes')}),
        ('Metadata', {'fields': ('created_by', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    fields = ['inventory_item', 'quantity', 'unit_price', 'total_price']
    readonly_fields = ['total_price']

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'vendor', 'status', 'issue_date', 'expected_delivery_date', 'total_amount')
    list_filter = ('status', 'issue_date')
    search_fields = ('order_number', 'vendor__vendor_name', 'notes')
    readonly_fields = ('total_amount', 'created_at', 'updated_at')
    inlines = [PurchaseOrderItemInline, VendorCommunicationInline]
    fieldsets = (
        (None, {'fields': ('vendor', 'order_number', 'status')}),
        ('Dates', {'fields': ('issue_date', 'expected_delivery_date', 'delivery_date')}),
        ('Financial', {'fields': ('total_amount', 'notes')}),
        ('Approval', {'fields': ('created_by', 'approved_by')}),
        ('Metadata', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    list_display = ('inventory_item', 'purchase_order', 'quantity', 'unit_price', 'total_price')
    list_filter = ('purchase_order__status',)
    search_fields = ('inventory_item__item_name', 'purchase_order__order_number', 'notes')
    readonly_fields = ['total_price']
    
@admin.register(VendorCommunication)
class VendorCommunicationAdmin(admin.ModelAdmin):
    list_display = ('subject', 'vendor', 'communication_type', 'date', 'user')
    list_filter = ('communication_type', 'date')
    search_fields = ('subject', 'message', 'vendor__vendor_name')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('vendor', 'purchase_order', 'communication_type')}),
        ('Message', {'fields': ('subject', 'message', 'date')}),
        ('Metadata', {'fields': ('user', 'created_at'), 'classes': ('collapse',)}),
    )
