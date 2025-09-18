from django.contrib import admin
from .models import Task, TaskComment, TaskAttachment

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'assigned_to', 'created_by', 'due_date')
    list_filter = ('status', 'priority', 'assigned_to', 'created_by')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    raw_id_fields = ('assigned_to', 'created_by')

@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('content', 'task__title')
    ordering = ('-created_at',)
    raw_id_fields = ('task', 'user')

@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ('task', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_by', 'uploaded_at')
    search_fields = ('description', 'task__title')
    ordering = ('-uploaded_at',)
    raw_id_fields = ('task', 'uploaded_by') 