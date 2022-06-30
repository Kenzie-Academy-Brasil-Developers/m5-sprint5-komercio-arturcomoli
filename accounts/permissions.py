import ipdb
from rest_framework import permissions


class AccountOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        return request.user.id == obj.id


class UpdateIsActive(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser
