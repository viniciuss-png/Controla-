from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user

        if hasattr(obj, "usuario"):
            return obj.usuario == user
        
        return False
