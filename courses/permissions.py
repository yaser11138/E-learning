from rest_framework.permissions import BasePermission


class IsInstructor(BasePermission):
    def has_permission(self, request, view):
        if hasattr(request.user, "instructor"):
            return True
        else:
            return False
