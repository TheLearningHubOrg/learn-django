from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Anyone may read; only the owner may change or delete an object."""

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner_id == request.user.id
