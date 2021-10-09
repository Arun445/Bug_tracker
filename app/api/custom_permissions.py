from rest_framework.permissions import BasePermission

SAFE_METHODS = ['GET']


class IsAdminOrReadOnly(BasePermission):
    """
    Only safe method are allowed if the user is not a superuser
    """

    def has_permission(self, request, view):

        if (request.method in SAFE_METHODS
            and request.user
                and request.user.is_authenticated):
            return True
        elif (request.user
              and request.user.is_staff
              and request.user.is_project_manager
              or request.user.is_superuser):
            return True
        return False


class IsSubmitterOrReadOnly(BasePermission):
    """
    Allows access only to submitter users.
    """

    def has_permission(self, request, view):

        if (request.method in SAFE_METHODS
            and request.user
                and request.user.is_authenticated):
            return True
        elif (request.user
              and request.user.is_staff
              and request.user.is_submitter
              or request.user.is_superuser):

            return True
        return False


class IsProjectManager(BasePermission):
    """
    Allows access only to project manager .
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_staff
            and request.user.is_project_manager
        )


class IsAdminUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):

        return bool(request.user and request.user.is_staff)
