from accounts.models import Role
from accounts.services.service_helper.accounts_service_helper import AccountsServiceHelper


class GetRolesService(AccountsServiceHelper):

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        data = kwargs.get("data")
        return {
            "page": int(data.get("page", 1)),
            "page_size": int(data.get("page_size", 10))
        }

    def get_data(self, *args, **kwargs):
        params = self.get_request_params(*args, **kwargs)

        roles = Role.objects.all()

        return {
            "roles": [
                {
                    "id": role.id,
                    "name": role.name,
                    "description": role.description,
                    "created_at": role.created_at.isoformat()
                }
                for role in roles
            ]
        }