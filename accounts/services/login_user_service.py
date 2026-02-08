import hashlib
import jwt
from datetime import datetime, timedelta
from rest_framework import status

from accounts.models import Users, UserProfile
from accounts.services.service_helper.accounts_service_helper import AccountsServiceHelper
from file_integrity_monitoring import settings
from file_integrity_monitoring.commons.commons import Commons
from file_integrity_monitoring.commons.generic_constants import GenericConstants


class LoginUserService(AccountsServiceHelper):

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        data = kwargs.get("data")
        return {
            "email": data.get("email"),
            "password": data.get("password")
        }

    def get_data(self, *args, **kwargs):
        params = self.get_request_params(*args, **kwargs)

        try:
            user = Users.objects.get(email=params.get("email"), is_active=True)
        except Users.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.INVALID_EMAIL_OR_PASSWORD_MESSAGE}

        hashed_password = hashlib.sha256((params.get("password") + settings.SECRET_KEY).encode()).hexdigest()

        if user.password != hashed_password:
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.INVALID_EMAIL_OR_PASSWORD_MESSAGE}

        if not user.is_active:
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.USER_INACTIVE_MESSAGE}

        user_profile = UserProfile.objects.get(user=user)

        api_token_payload = {
            "user_id": user.id,
            "email": user.email,
            "role": user_profile.role.name,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow()
        }

        refresh_token_payload = {
            "user_id": user.id,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(days=7),
            "iat": datetime.utcnow()
        }

        api_token = jwt.encode(api_token_payload, settings.SECRET_KEY, algorithm="HS256")
        refresh_token = jwt.encode(refresh_token_payload, settings.SECRET_KEY, algorithm="HS256")

        Commons.create_audit_log(
            user_id=user.id,
            action="login",
            resource_type="Users",
            resource_id=user.id,
            new_values={"email": user.email}
        )

        return {
            "message": GenericConstants.LOGIN_SUCCESSFUL_MESSAGE,
            "user_id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role_id": user_profile.role.id,
            "api_token": api_token,
            "refresh_token": refresh_token
        }