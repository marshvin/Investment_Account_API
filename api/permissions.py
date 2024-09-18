from rest_framework import permissions
from .models import UserAccountPermission
import logging

logger = logging.getLogger(__name__)

class AccountPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        logger.debug(f"Checking permission for user: {user}")

        if not user.is_authenticated:
            logger.debug("User is not authenticated")
            return False

        if view.action == 'list':
            # Allow list action, but filter results in get_queryset
            return True

        # For create action, we need to check the account from the request data
        if view.action == 'create':
            account_id = request.data.get('account')
        else:
            account_id = view.kwargs.get('pk')

        logger.debug(f"Account ID from request: {account_id}")

        if not account_id:
            logger.debug("No account ID found in request")
            return False

        try:
            account_id = int(account_id)
        except ValueError:
            logger.debug("Invalid account ID")
            return False

        permission = UserAccountPermission.objects.filter(user=user, account_id=account_id).first()
        logger.debug(f"User: {user}, Account: {account_id}, Permission: {permission.permission if permission else 'None'}")

        if not permission:
            logger.debug("No permission found for user and account")
            return False

        if view.action in ['retrieve', 'list']:
            allowed = permission.permission in [UserAccountPermission.VIEW_ONLY, UserAccountPermission.CRUD]
        elif view.action == 'create':
            allowed = permission.permission in [UserAccountPermission.POST_ONLY, UserAccountPermission.CRUD]
        elif view.action in ['update', 'partial_update', 'destroy']:
            allowed = permission.permission == UserAccountPermission.CRUD
        else:
            allowed = False

        logger.debug(f"Permission check result for action {view.action}: {allowed}")
        return allowed

    def has_object_permission(self, request, view, obj):
        # This method is called for object-level permissions
        return self.has_permission(request, view)