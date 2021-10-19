from rest_framework.permissions import BasePermission


class IsDriver(BasePermission):
    """
    Allows access only to Drivers.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.type)


class IsApplicant(BasePermission):
    """
    Allows access only to Applicants.
    """

    def has_permission(self, request, view):
        return bool(request.user and not request.user.type)
