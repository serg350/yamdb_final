from rest_framework import permissions


class AdminOrMyselfOnly(permissions.BasePermission):
    """
    Разрешение пользователям изменять свой профиль,
    у администраторов полный доступ.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class AdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение "только для чтения" для всех, у администраторов полный доступ.
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and request.user.is_admin
        )


class AdminOrModeratorOrAuthor(permissions.IsAuthenticatedOrReadOnly):
    """
    Разрешение пользователям управлять отзывами и комментариями,
    у администраторов и модераторов полный доступ.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and (
                request.user.is_admin
                or request.user.is_moderator
                or obj.author == request.user
            )
        )
