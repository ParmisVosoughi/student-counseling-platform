from rest_framework.permissions import BasePermission

def is_admin(user): return bool(user and user.is_authenticated and user.role=='ADMIN')
def is_supervisor(user): return bool(user and user.is_authenticated and user.role=='SUPERVISOR')
def is_advisor(user): return bool(user and user.is_authenticated and user.role=='ADVISOR')

class IsAdmin(BasePermission):
    def has_permission(self, request, view): return is_admin(request.user)
class IsSupervisorOrAdmin(BasePermission):
    def has_permission(self, request, view): return is_admin(request.user) or is_supervisor(request.user)
