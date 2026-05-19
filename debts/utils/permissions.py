from rest_framework.permissions import BasePermission
# Enter your code here.


class IsDebtorOrCreditor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.creditor or request.user == obj.debtor
    

class IsDebtor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.debtor
    

class IsCreditor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.creditor
