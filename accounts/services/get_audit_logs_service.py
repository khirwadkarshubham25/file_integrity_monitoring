from rest_framework import status

from accounts.models import AuditLogs
from accounts.services.service_helper.accounts_service_helper import AccountsServiceHelper


class GetAuditLogsService(AccountsServiceHelper):

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        data = kwargs.get("data")
        return {
            "page": int(data.get("page", 1)),
            "page_size": int(data.get("page_size", 10)),
            "sort_by": data.get("sort_by", "created_at"),
            "sort_order": data.get("sort_order", "desc"),
            "action": data.get("action"),
            "resource_type": data.get("resource_type")
        }

    def get_data(self, *args, **kwargs):
        params = self.get_request_params(*args, **kwargs)

        sort_by = params.get("sort_by")
        if params.get("sort_order") == "desc":
            sort_by = f"-{sort_by}"

        audit_logs = AuditLogs.objects.all()

        if params.get("action"):
            audit_logs = audit_logs.filter(action=params.get("action"))

        if params.get("resource_type"):
            audit_logs = audit_logs.filter(resource_type=params.get("resource_type"))

        audit_logs = audit_logs.order_by(sort_by).select_related('user')

        page = params.get("page")
        page_size = params.get("page_size")
        start = (page - 1) * page_size
        end = start + page_size

        paginated_logs = audit_logs[start:end]

        return {
            "audit_logs": [
                {
                    "id": log.id,
                    "user_email": log.user.email if log.user else None,
                    "user_first_name": log.user.first_name if log.user else None,
                    "user_last_name": log.user.last_name if log.user else None,
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "ip_address": log.ip_address,
                    "created_at": log.created_at.isoformat()
                }
                for log in paginated_logs
            ],
            "total": audit_logs.count(),
            "page": page,
            "page_size": page_size
        }