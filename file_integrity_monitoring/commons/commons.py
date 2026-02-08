from django.test import RequestFactory

from accounts.services.create_audit_logs_service import CreateAuditLogsService


class Commons:
    def __init__(self):
        pass

    @staticmethod
    def create_audit_log(user_id, action, resource_type, resource_id, old_values=None, new_values=None):
        factory = RequestFactory()
        request = factory.get('/')

        data = {
            'user_id': user_id,
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'old_values': old_values,
            'new_values': new_values
        }

        service = CreateAuditLogsService()
        service.execute_service(request=request, data=data)

        return service.data