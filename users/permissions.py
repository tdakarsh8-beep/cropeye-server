from rest_framework import permissions


class HasRolePermission(permissions.BasePermission):
    """
    Generic permission that checks if the user has any of the given roles.
    Set `roles` in subclasses.
    """
    roles = []

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and (
            user.is_superuser or user.has_any_role(self.roles)
        )


class IsSuperAdmin(HasRolePermission):
    roles = ['admin']


class IsAdmin(HasRolePermission):
    roles = ['admin']


class IsManager(permissions.BasePermission):
    """
    Custom permission to only allow managers to access.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.has_role('manager')
        )


class IsAgronomist(HasRolePermission):
    roles = ['agronomist']


class IsQualityControl(HasRolePermission):
    roles = ['qualitycontrol']


class IsFieldOfficer(permissions.BasePermission):
    """
    Custom permission to only allow field officers to access.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.has_role('fieldofficer')
        )


class IsFarmer(permissions.BasePermission):
    """
    Custom permission to only allow farmers to access.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.has_role('farmer')
        )


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners to access.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.has_role('owner')
        )


class IsOwnerOrManager(permissions.BasePermission):
    """
    Custom permission to allow owners or managers to access.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.has_any_role(['owner', 'manager'])
        )
