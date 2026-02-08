import hashlib

from rest_framework import status

from accounts.models import Users, UserProfile, Role
from accounts.services.service_helper.accounts_service_helper import AccountsServiceHelper
from file_integrity_monitoring import settings
from file_integrity_monitoring.commons.commons import Commons
from file_integrity_monitoring.commons.generic_constants import GenericConstants


class RegisterUserService(AccountsServiceHelper):

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        data = kwargs.get("data")
        return {
            "email": data.get("email"),
            "password": data.get("password"),
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
        }

    def get_data(self, *args, **kwargs):

        params = self.get_request_params(*args, **kwargs)

        if Users.objects.filter(email=params.get("email")).exists():
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.EMAIL_ALREADY_EXISTS_MESSAGE}

        try:
            role = Role.objects.get(id=1)
        except Role.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.INVALID_ROLE_MESSAGE}

        hashed_password = hashlib.sha256((params.get("password") + settings.SECRET_KEY).encode()).hexdigest()

        user = Users.objects.create(
            email=params.get("email"),
            password=hashed_password,
            first_name=params.get("first_name"),
            last_name=params.get("last_name")
        )

        UserProfile.objects.create(user=user, role=role)

        Commons.create_audit_log(
            user_id=user.id,
            action="create",
            resource_type="Users",
            resource_id=user.id,
            new_values={"email": user.email, "role_id": role.id}
        )

        return {
            "message": GenericConstants.REGISTER_USER_SUCCESSFUL_MESSAGE
        }