from django.contrib import admin
from .models import Booking, BookingComment, BookingAttachment

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('title', 'booking_type', 'status', 'created_by', 'approved_by', 'start_date', 'end_date')
    list_filter = ('booking_type', 'status', 'created_by', 'approved_by')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    raw_id_fields = ('created_by', 'approved_by')

@admin.register(BookingComment)
class BookingCommentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'user', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('content', 'booking__title')
    ordering = ('-created_at',)
    raw_id_fields = ('booking', 'user')

@admin.register(BookingAttachment)
class BookingAttachmentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_by', 'uploaded_at')
    search_fields = ('description', 'booking__title')
    ordering = ('-uploaded_at',)
    raw_id_fields = ('booking', 'uploaded_by') 