from rest_framework import status

from accounts.models import AuditLogs, Users
from accounts.services.service_helper.accounts_service_helper import AccountsServiceHelper
from file_integrity_monitoring.commons.generic_constants import GenericConstants


class CreateAuditLogsService(AccountsServiceHelper):

    def __init__(self):
        super().__init__()

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_request_params(self, *args, **kwargs):
        data = kwargs.get("data")
        request = kwargs.get("request")

        ip_address = self.get_client_ip(request) if request else None

        return {
            "user_id": data.get("user_id"),
            "action": data.get("action"),
            "resource_type": data.get("resource_type"),
            "resource_id": data.get("resource_id"),
            "ip_address": ip_address,
            "old_values": data.get("old_values"),
            "new_values": data.get("new_values")
        }

    def get_data(self, *args, **kwargs):
        params = self.get_request_params(*args, **kwargs)

        try:
            user = Users.objects.get(id=params.get("user_id")) if params.get("user_id") else None
        except Users.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.USER_NOT_FOUND_MESSAGE}

        audit_log = AuditLogs.objects.create(
            user=user,
            action=params.get("action"),
            resource_type=params.get("resource_type"),
            resource_id=params.get("resource_id"),
            ip_address=params.get("ip_address"),
            old_values=params.get("old_values"),
            new_values=params.get("new_values")
        )

        return {
            "message": GenericConstants.AUDIT_LOG_CREATE_SUCCESSFUL_MESSAGE
        }