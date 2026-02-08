from rest_framework import status

from accounts.services.create_role_service import CreateRoleService
from accounts.services.create_users_service import CreateUsersService
from accounts.services.delete_role_service import DeleteRoleService
from accounts.services.delete_users_service import DeleteUsersService
from accounts.services.get_audit_log_details_service import GetAuditLogDetailsService
from accounts.services.get_audit_logs_service import GetAuditLogsService
from accounts.services.get_roles_service import GetRolesService
from accounts.services.get_user_details_service import GetUserDetailsService
from accounts.services.get_users_service import GetUsersService
from accounts.services.login_user_service import LoginUserService
from accounts.services.register_user_service import RegisterUserService
from accounts.services.update_role_service import UpdateRoleService
from accounts.services.update_users_service import UpdateUsersService


class ViewServices:

    def __init__(self, service_name=None):
        self.service_config = {
            'get_roles': self.GetRoles,
            'create_role': self.CreateRole,
            'update_role': self.UpdateRole,
            'delete_role': self.DeleteRole,

            'register_user': self.RegisterUser,
            'login_user': self.LoginUser,

            'get_users': self.GetUsers,
            'get_user_details': self.GetUserDetails,
            'create_users': self.CreateUsers,
            'update_users': self.UpdateUsers,
            'delete_users': self.DeleteUsers,

            'get_audit_logs': self.GetAuditLogs,
            'get_audit_log_details': self.GetAuditLogDetails
        }
        self.service_obj = self.service_config[service_name].get_instance()

    def execute_service(self, *args, **kwargs):
        self.service_obj.execute_service(*args, **kwargs)
        if self.service_obj.status_code is not None:
            status_code = self.service_obj.status_code
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR if self.service_obj.error else status.HTTP_200_OK
        data = self.service_obj.data

        return status_code, data

    class GetRoles:
        @staticmethod
        def get_instance():
            return GetRolesService()

    class CreateRole:
        @staticmethod
        def get_instance():
            return CreateRoleService()

    class UpdateRole:
        @staticmethod
        def get_instance():
            return UpdateRoleService()

    class DeleteRole:
        @staticmethod
        def get_instance():
            return DeleteRoleService()

    class RegisterUser:
        @staticmethod
        def get_instance():
            return RegisterUserService()

    class LoginUser:
        @staticmethod
        def get_instance():
            return LoginUserService()

    class GetUsers:
        @staticmethod
        def get_instance():
            return GetUsersService()

    class GetUserDetails:
        @staticmethod
        def get_instance():
            return GetUserDetailsService()

    class CreateUsers:
        @staticmethod
        def get_instance():
            return CreateUsersService()

    class UpdateUsers:
        @staticmethod
        def get_instance():
            return UpdateUsersService()

    class DeleteUsers:
        @staticmethod
        def get_instance():
            return DeleteUsersService()

    class GetAuditLogs:
        @staticmethod
        def get_instance():
            return GetAuditLogsService()

    class GetAuditLogDetails:
        @staticmethod
        def get_instance():
            return GetAuditLogDetailsService()
