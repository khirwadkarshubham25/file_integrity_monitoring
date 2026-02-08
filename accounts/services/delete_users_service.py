from rest_framework import status

from accounts.models import Users
from accounts.services.service_helper.accounts_service_helper import AccountsServiceHelper
from file_integrity_monitoring.commons.commons import Commons
from file_integrity_monitoring.commons.generic_constants import GenericConstants


class DeleteUsersService(AccountsServiceHelper):

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        data = kwargs.get("data")
        return {
            "admin_user_id": data.get("admin_user_id"),
            "user_id": data.get("user_id")
        }

    def get_data(self, *args, **kwargs):
        params = self.get_request_params(*args, **kwargs)

        try:
            user = Users.objects.get(id=params.get("user_id"))
        except Users.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_404_NOT_FOUND)
            return {"message": GenericConstants.USER_NOT_FOUND_MESSAGE}

        user.delete()

        Commons.create_audit_log(
            user_id=params.get("admin_user_id"),
            action="delete",
            resource_type="Users",
            resource_id=params.get("user_id"),
            old_values={"email": user.email}
        )

        return {
            "message": GenericConstants.USER_DELETED_SUCCESSFUL_MESSAGE
        }