from rest_framework import status

from accounts.models import Users, UserProfile
from accounts.services.service_helper.accounts_service_helper import AccountsServiceHelper


class GetUsersService(AccountsServiceHelper):

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        data = kwargs.get("data")
        return {
            "page": int(data.get("page", 1)),
            "page_size": int(data.get("page_size", 10)),
            "sort_by": data.get("sort_by", "created_at"),
            "sort_order": data.get("sort_order", "desc")
        }

    def get_data(self, *args, **kwargs):
        params = self.get_request_params(*args, **kwargs)

        sort_by = params.get("sort_by")
        if params.get("sort_order") == "desc":
            sort_by = f"-{sort_by}"

        users = Users.objects.all().order_by(sort_by)

        page = params.get("page")
        page_size = params.get("page_size")
        start = (page - 1) * page_size
        end = start + page_size

        paginated_users = users[start:end]

        users_data = []
        for user in paginated_users:
            user_dict = {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat()
            }

            # Get role name from UserProfile
            try:
                user_profile = UserProfile.objects.get(user=user)
                user_dict["role_name"] = user_profile.role.name
                user_dict["role_id"] = user_profile.role.id
            except UserProfile.DoesNotExist:
                user_dict["role_name"] = "N/A"
                user_dict["role_id"] = None

            users_data.append(user_dict)

        self.set_status_code(status_code=status.HTTP_200_OK)
        return {
            "users": users_data,
            "total": users.count(),
            "page": page,
            "page_size": page_size
        }