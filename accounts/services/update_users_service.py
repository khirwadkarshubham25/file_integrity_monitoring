import hashlib

from rest_framework import status

from accounts.models import Users, UserProfile, Role
from accounts.services.service_helper.accounts_service_helper import AccountsServiceHelper
from file_integrity_monitoring import settings
from file_integrity_monitoring.commons.commons import Commons
from file_integrity_monitoring.commons.generic_constants import GenericConstants


class UpdateUsersService(AccountsServiceHelper):

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        data = kwargs.get("data")
        return {
            "admin_user_id": data.get("admin_user_id"),
            "user_id": data.get("user_id"),
            "email": data.get("email"),
            "password": data.get("password"),
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "role_id": data.get("role_id"),
            "is_active": data.get("is_active")
        }

    def get_data(self, *args, **kwargs):
        params = self.get_request_params(*args, **kwargs)

        try:
            user = Users.objects.get(id=params.get("user_id"))
        except Users.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_404_NOT_FOUND)
            return {"message": GenericConstants.USER_NOT_FOUND_MESSAGE}

        if params.get("email") and params.get("email") != user.email:
            if Users.objects.filter(email=params.get("email")).exists():
                self.error = True
                self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
                return {"message": GenericConstants.EMAIL_ALREADY_EXISTS_MESSAGE}
            user.email = params.get("email")

        if params.get("password"):
            hashed_password = hashlib.sha256((params.get("password") + settings.SECRET_KEY).encode()).hexdigest()
            user.password = hashed_password

        if params.get("first_name"):
            user.first_name = params.get("first_name")

        if params.get("last_name"):
            user.last_name = params.get("last_name")

        if params.get("is_active") is not None:
            user.is_active = params.get("is_active")

        user.save()

        if params.get("role_id"):
            try:
                role = Role.objects.get(id=params.get("role_id"))
                user_profile = UserProfile.objects.get(user=user)
                user_profile.role = role
                user_profile.save()
            except (Role.DoesNotExist, UserProfile.DoesNotExist):
                self.error = True
                self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
                return {"message": GenericConstants.INVALID_ROLE_MESSAGE}

        Commons.create_audit_log(
            user_id=params.get("admin_user_id"),
            action="update",
            resource_type="Users",
            resource_id=user.id,
            new_values={"email": user.email}
        )

        return {
            "message": GenericConstants.USER_UPDATED_SUCCESSFUL_MESSAGE
        }