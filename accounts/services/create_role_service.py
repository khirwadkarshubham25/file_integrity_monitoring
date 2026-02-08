from rest_framework import status

from accounts.models import Role
from accounts.services.service_helper.accounts_service_helper import AccountsServiceHelper
from file_integrity_monitoring.commons.commons import Commons
from file_integrity_monitoring.commons.generic_constants import GenericConstants


class CreateRoleService(AccountsServiceHelper):

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        data = kwargs.get("data")
        return {
            "admin_user_id": data.get("admin_user_id"),
            "name": data.get("name"),
            "description": data.get("description", "")
        }

    def get_data(self, *args, **kwargs):
        params = self.get_request_params(*args, **kwargs)

        if Role.objects.filter(name=params.get("name")).exists():
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.ROLE_ALREADY_EXISTS_MESSAGE}

        role = Role.objects.create(
            name=params.get("name"),
            description=params.get("description")
        )

        Commons.create_audit_log(
            user_id=params.get("admin_user_id"),
            action="create",
            resource_type="Role",
            resource_id=role.id,
            new_values={"name": role.name}
        )

        return {
            "message": GenericConstants.ROLE_CREATED_SUCCESSFUL_MESSAGE
        }