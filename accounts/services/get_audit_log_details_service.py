from rest_framework import status

from accounts.models import AuditLogs
from accounts.services.service_helper.accounts_service_helper import AccountsServiceHelper
from file_integrity_monitoring.commons.generic_constants import GenericConstants


class GetAuditLogDetailsService(AccountsServiceHelper):

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        data = kwargs.get("data")
        return {
            "log_id": data.get("log_id")
        }

    def get_data(self, *args, **kwargs):
        params = self.get_request_params(*args, **kwargs)

        try:
            audit_log = AuditLogs.objects.select_related('user').get(id=params.get("log_id"))
        except AuditLogs.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_404_NOT_FOUND)
            return {"message": GenericConstants.AUDIT_LOG_NOT_FOUND_MESSAGE}

        self.set_status_code(status_code=status.HTTP_200_OK)
        return {
            "audit_log": {
                "id": audit_log.id,
                "user_email": audit_log.user.email if audit_log.user else None,
                "user_first_name": audit_log.user.first_name if audit_log.user else None,
                "user_last_name": audit_log.user.last_name if audit_log.user else None,
                "action": audit_log.action,
                "resource_type": audit_log.resource_type,
                "resource_id": audit_log.resource_id,
                "old_values": audit_log.old_values,
                "new_values": audit_log.new_values,
                "ip_address": audit_log.ip_address,
                "created_at": audit_log.created_at.isoformat()
            }
        }