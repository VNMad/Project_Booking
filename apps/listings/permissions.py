from rest_framework.permissions import BasePermission, SAFE_METHODS, DjangoModelPermissions


class IsOwnerOrReadOnly(BasePermission):
    """
    Permission class that allows public read access and restricts write operations to the object owner.

    Safe HTTP methods such as GET, HEAD, and OPTIONS are available to everyone.

    For write operations, the authenticated user must be the owner of the listing.
    For Photo objects, ownership is checked through the related listing.
    """

    def has_permission(self, request, view):
        """
        Check whether the user is allowed to access the view.

        Read-only requests are allowed for everyone.
        Write requests require an authenticated user.
        """
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check whether the user can access a specific object.
        Read-only requests are allowed for everyone. Write operations are allowed only to the listing owner.
        Listing objects store the owner directly in owner_id.
        Photo objects obtain the owner through their related listing.
        """
        if request.method in SAFE_METHODS:
            return True

        if hasattr(obj, "owner_id"):
            return obj.owner_id == request.user.id

        return obj.listing.owner_id == request.user.id


class ModelPermissions(DjangoModelPermissions):
    """
    Extended Django model permissions for REST API operations.
    In addition to the standard DjangoModelPermissions mapping, GET requests require the model's view permission.
    The permission mapping is based on the standard Django add, change, and delete permissions.
    """
    perms_map = {
        **DjangoModelPermissions.perms_map,
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }