from rest_framework import permissions

class AdminPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.auth.payload['role'] == 1:
            return True
        
        return False