from rest_framework import status

from accounts.models import Role
from accounts.services.service_helper.accounts_service_helper import AccountsServiceHelper
from file_integrity_monitoring.commons.commons import Commons
from file_integrity_monitoring.commons.generic_constants import GenericConstants


class DeleteRoleService(AccountsServiceHelper):

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        data = kwargs.get("data")
        return {
            "admin_user_id": data.get("admin_user_id"),
            "role_id": data.get("role_id")
        }

    def get_data(self, *args, **kwargs):
        params = self.get_request_params(*args, **kwargs)

        try:
            role = Role.objects.get(id=params.get("role_id"))
        except Role.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_404_NOT_FOUND)
            return {"message": GenericConstants.ROLE_NOT_FOUND_MESSAGE}

        role.delete()

        Commons.create_audit_log(
            user_id=params.get("admin_user_id"),
            action="delete",
            resource_type="Role",
            resource_id=params.get("role_id"),
            old_values={"name": role.name}
        )

        return {
            "message": GenericConstants.ROLE_DELETE_SUCCESSFUL_MESSAGE
        }