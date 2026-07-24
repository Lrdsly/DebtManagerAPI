from rest_framework.permissions import BasePermission

from users.models import MemberShip
# Enter your code here.


class IsOwner(BasePermission):
    """ only object owner has permission """
  
    def has_object_permission(self, request, view, obj):
        return request.user == obj
    
    def has_permission(self, request, view):
        return request.user.is_authenticated


class IsRoomAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.admin
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    

class IsMember(BasePermission):
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        return MemberShip.objects.filter(user=request.user, room=obj).exists()
