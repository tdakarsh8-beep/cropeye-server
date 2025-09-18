from rest_framework import permissions
from users.permissions import IsSuperAdmin, IsManager, IsFieldOfficer



class CanManageEquipment(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            (request.user.is_super_admin or
             request.user.is_manager or
             request.user.is_field_officer)
        )

class CanViewEquipment(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_super_admin or
            request.user.is_manager or
            request.user.is_field_officer or
            obj.assigned_to == request.user
        ) 