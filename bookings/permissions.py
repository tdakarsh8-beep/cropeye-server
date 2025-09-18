from rest_framework import permissions
from users.permissions import IsSuperAdmin, IsManager

class CanManageBookings(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.is_super_admin or
             request.user.is_manager)
        )

class CanViewBookings(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_super_admin or
            request.user.is_manager or
            obj.created_by == request.user or
            obj.booking_type == 'public'
        ) 