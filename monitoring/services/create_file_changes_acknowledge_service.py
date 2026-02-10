from rest_framework import status

from monitoring.models import FileChange
from accounts.models import Users
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper
from file_integrity_monitoring.commons.generic_constants import GenericConstants
from file_integrity_monitoring.commons.commons import Commons


class CreateFileChangesAcknowledgeService(MonitoringServiceHelper):
    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        data = kwargs.get("data")
        return {
            "change_id": data.get("file_change_id"),
            "acknowledged_reason": data.get("acknowledged_reason", ""),
            "user_id": data.get("user_id")
        }

    def get_data(self, *args, **kwargs):
        params = self.get_request_params(*args, **kwargs)

        if not params.get("change_id"):
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.FILE_CHANGE_ID_REQUIRED_MESSAGE}

        # Validate user_id
        if not params.get("user_id"):
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.USER_ID_REQUIRED_MESSAGE}

        # Get file change
        try:
            change = FileChange.objects.get(id=params.get("change_id"))
        except FileChange.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_404_NOT_FOUND)
            return {"message": GenericConstants.FILE_CHANGE_NOT_FOUND_MESSAGE}

        # Check if user exists
        try:
            user = Users.objects.get(id=params.get("user_id"))
        except Users.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.USER_NOT_FOUND_MESSAGE}

        # Store old values for audit log
        old_acknowledged = change.acknowledged
        old_acknowledged_reason = change.acknowledged_reason

        # Acknowledge the change
        change.acknowledged = True
        change.user = user
        change.acknowledged_reason = params.get("acknowledged_reason", "")
        change.save()

        # Create audit log
        Commons.create_audit_log(
            user_id=params.get("user_id"),
            action="acknowledge",
            resource_type="FileChange",
            resource_id=change.id,
            old_values={
                "acknowledged": old_acknowledged,
                "acknowledged_reason": old_acknowledged_reason
            },
            new_values={
                "acknowledged": True,
                "acknowledged_reason": change.acknowledged_reason,
                "file_path": change.file_path,
                "change_type": change.change_type
            }
        )

        return {
            "message": GenericConstants.FILE_ACKNOWLEDGE_SUCCESSFUL_MESSAGE,
        }