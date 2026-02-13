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
from monitoring.services.alert_archive_create_service import AlertArchiveCreateService
from monitoring.services.baseline_create_service import BaselineCreateService
from monitoring.services.baseline_get_details_service import BaselineGetDetailsService
from monitoring.services.file_changes_acknowledge_create_service import CreateFileChangesAcknowledgeService
from monitoring.services.create_whitelist_rule_service import WhitelistRuleCreateService
from monitoring.services.baseline_delete_service import BaselineDeleteService
from monitoring.services.whitelist_rule_delete_service import WhitelistRuleDeleteService
from monitoring.services.alert_details_get_service import AlertDetailsGetService
from monitoring.services.alerts_get_service import AlertsGetService
from monitoring.services.baseline_get_service import BaselineGetService
from monitoring.services.dashboard_summary_get_service import DashboardSummaryGetService
from monitoring.services.file_change_details_get_service import FileChangeDetailsGetService
from monitoring.services.file_changes_get_service import FileChangesGetService
from monitoring.services.monitoring_session_details_get_service import MonitoringSessionDetailsGetService
from monitoring.services.monitoring_sessions_get_service import MonitoringSessionsGetService
from monitoring.services.whiltelist_rule_details_get_service import WhitelistRuleDetailsGetService
from monitoring.services.whitelist_rules_get_service import WhitelistRulesGetService
from monitoring.services.alert_mark_read_create_service import AlertMarkReadCreateService
from monitoring.services.monitoring_session_create_service import MonitoringSessionCreateService
from monitoring.services.baseline_update_service import BaselineUpdateService
from monitoring.services.whitelist_rule_update_service import WhitelistRuleUpdateService


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
            'get_audit_log_details': self.GetAuditLogDetails,

            'get_dashboard_summary': self.GetDashboardSummary,
            'get_baselines': self.GetBaselines,
            'create_baseline': self.CreateBaseline,
            'update_baseline': self.UpdateBaseline,
            'delete_baseline': self.DeleteBaseline,
            'get_baseline_details': self.GetBaselineDetails,
            'get_alerts': self.GetAlerts,
            'get_alert_details': self.GetAlertDetails,
            'mark_alert_read': self.MarkAlertRead,
            'archive_alert': self.ArchiveAlertRead,
            'get_file_changes': self.GetFileChanges,
            'get_file_change_details': self.GetFileChangeDetails,
            'acknowledge_file_change': self.AcknowledgeFileChange,
            'get_monitoring_sessions': self.GetMonitoringSessions,
            'get_monitoring_session_details': self.GetMonitoringSessionDetails,
            'start_monitoring_session': self.StartMonitoringSession,
            'get_whitelist_rules': self.GetWhitelistRules,
            'create_whitelist_rule': self.CreateWhitelistRule,
            'update_whitelist_rule': self.UpdateWhitelistRule,
            'delete_whitelist_rule': self.DeleteWhitelistRule,
            'get_whitelist_rule_details': self.GetWhitelistRuleDetails
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

    class GetDashboardSummary:
        @staticmethod
        def get_instance():
            return DashboardSummaryGetService()

    class GetBaselines:
        @staticmethod
        def get_instance():
            return BaselineGetService()

    class CreateBaseline:
        @staticmethod
        def get_instance():
            return BaselineCreateService()

    class UpdateBaseline:
        @staticmethod
        def get_instance():
            return BaselineUpdateService()

    class DeleteBaseline:
        @staticmethod
        def get_instance():
            return BaselineDeleteService()

    class GetBaselineDetails:
        @staticmethod
        def get_instance():
            return BaselineGetDetailsService()

    class GetAlerts:
        @staticmethod
        def get_instance():
            return AlertsGetService()

    class GetAlertDetails:
        @staticmethod
        def get_instance():
            return AlertDetailsGetService()

    class MarkAlertRead:
        @staticmethod
        def get_instance():
            return AlertMarkReadCreateService()

    class ArchiveAlertRead:
        @staticmethod
        def get_instance():
            return AlertArchiveCreateService()

    class GetFileChanges:
        @staticmethod
        def get_instance():
            return FileChangesGetService()

    class GetFileChangeDetails:
        @staticmethod
        def get_instance():
            return FileChangeDetailsGetService()

    class AcknowledgeFileChange:
        @staticmethod
        def get_instance():
            return CreateFileChangesAcknowledgeService()

    class GetMonitoringSessions:
        @staticmethod
        def get_instance():
            return MonitoringSessionsGetService()

    class GetMonitoringSessionDetails:
        @staticmethod
        def get_instance():
            return MonitoringSessionDetailsGetService()

    class StartMonitoringSession:
        @staticmethod
        def get_instance():
            return MonitoringSessionCreateService()

    class GetWhitelistRules:
        @staticmethod
        def get_instance():
            return WhitelistRulesGetService()

    class CreateWhitelistRule:
        @staticmethod
        def get_instance():
            return WhitelistRuleCreateService()

    class UpdateWhitelistRule:
        @staticmethod
        def get_instance():
            return WhitelistRuleUpdateService()

    class DeleteWhitelistRule:
        @staticmethod
        def get_instance():
            return WhitelistRuleDeleteService()

    class GetWhitelistRuleDetails:
        @staticmethod
        def get_instance():
            return WhitelistRuleDetailsGetService()