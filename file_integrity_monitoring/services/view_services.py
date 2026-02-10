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
from monitoring.services.archive_alert_service import ArchiveAlertService
from monitoring.services.create_baseline_service import CreateBaselineService
from monitoring.services.create_file_changes_acknowledge_service import CreateFileChangesAcknowledgeService
from monitoring.services.create_whitelist_rule_service import CreateWhitelistRuleService
from monitoring.services.delete_baseline_service import DeleteBaselineService
from monitoring.services.delete_whitelist_rule_service import DeleteWhitelistRuleService
from monitoring.services.get_alert_details_service import GetAlertDetailsService
from monitoring.services.get_alerts_service import GetAlertsService
from monitoring.services.get_baselines_service import GetBaselinesService
from monitoring.services.get_dashboard_summary_service import GetDashboardSummaryService
from monitoring.services.get_file_change_details_service import GetFileChangeDetailsService
from monitoring.services.get_file_changes_service import GetFileChangesService
from monitoring.services.get_monitoring_session_details_service import GetMonitoringSessionDetailsService
from monitoring.services.get_monitoring_sessions_service import GetMonitoringSessionsService
from monitoring.services.get_whiltelist_rule_details_service import GetWhitelistRuleDetailsService
from monitoring.services.get_whitelist_rules_service import GetWhitelistRulesService
from monitoring.services.mark_alert_read_service import MarkAlertReadService
from monitoring.services.monitoring_session_service import MonitoringSessionService
from monitoring.services.update_baseline_service import UpdateBaselineService
from monitoring.services.update_whitelist_rule_service import UpdateWhitelistRuleService


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
            return GetDashboardSummaryService()

    class GetBaselines:
        @staticmethod
        def get_instance():
            return GetBaselinesService()

    class CreateBaseline:
        @staticmethod
        def get_instance():
            return CreateBaselineService()

    class UpdateBaseline:
        @staticmethod
        def get_instance():
            return UpdateBaselineService()

    class DeleteBaseline:
        @staticmethod
        def get_instance():
            return DeleteBaselineService()

    class GetAlerts:
        @staticmethod
        def get_instance():
            return GetAlertsService()

    class GetAlertDetails:
        @staticmethod
        def get_instance():
            return GetAlertDetailsService()

    class MarkAlertRead:
        @staticmethod
        def get_instance():
            return MarkAlertReadService()

    class ArchiveAlertRead:
        @staticmethod
        def get_instance():
            return ArchiveAlertService()

    class GetFileChanges:
        @staticmethod
        def get_instance():
            return GetFileChangesService()

    class GetFileChangeDetails:
        @staticmethod
        def get_instance():
            return GetFileChangeDetailsService()

    class AcknowledgeFileChange:
        @staticmethod
        def get_instance():
            return CreateFileChangesAcknowledgeService()

    class GetMonitoringSessions:
        @staticmethod
        def get_instance():
            return GetMonitoringSessionsService()

    class GetMonitoringSessionDetails:
        @staticmethod
        def get_instance():
            return GetMonitoringSessionDetailsService()

    class StartMonitoringSession:
        @staticmethod
        def get_instance():
            return MonitoringSessionService()

    class GetWhitelistRules:
        @staticmethod
        def get_instance():
            return GetWhitelistRulesService()

    class CreateWhitelistRule:
        @staticmethod
        def get_instance():
            return CreateWhitelistRuleService()

    class UpdateWhitelistRule:
        @staticmethod
        def get_instance():
            return UpdateWhitelistRuleService()

    class DeleteWhitelistRule:
        @staticmethod
        def get_instance():
            return DeleteWhitelistRuleService()

    class GetWhitelistRuleDetails:
        @staticmethod
        def get_instance():
            return GetWhitelistRuleDetailsService()