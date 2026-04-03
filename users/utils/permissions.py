from rest_framework.permissions import BasePermission
# Enter your code here.


class IsOwner(BasePermission):
    """ only object owner has permission """
  
    def has_object_permission(self, request, view, obj):
        return request.user == obj
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
