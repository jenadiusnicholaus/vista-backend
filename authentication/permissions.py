from rest_framework import permissions

from host_data.models import PropertyHost

class IsHost(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_permission(self, request, view):
        try:

            isVerified =  PropertyHost.objects.get(user=request.user).is_verified
        except PropertyHost.DoesNotExist:
            isVerified = False

        if request.user.groups.filter(name='host').exists() and isVerified:
             return True
        else:
            return False