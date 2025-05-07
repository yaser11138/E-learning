from rest_framework.permissions import BasePermission


class IsInstructor(BasePermission):
    def has_permission(self, request, view):
        if hasattr(request.user, "instructor"):
            return True
        else:
            return False


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        if hasattr(request.user, "student"):
            return True
        else:
            return False


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj=None):
        if request.user == obj.owner:
            return True
        else:
            return False



