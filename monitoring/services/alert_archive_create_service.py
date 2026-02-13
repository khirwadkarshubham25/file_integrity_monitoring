from rest_framework import status

from monitoring.models import Alert
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper
from file_integrity_monitoring.commons.generic_constants import GenericConstants
from file_integrity_monitoring.commons.commons import Commons


class AlertArchiveCreateService(MonitoringServiceHelper):
    """Service to archive an alert"""

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        """Extract and validate alert archive parameters"""
        data = kwargs.get("data")
        return {
            "alert_id": data.get("alert_id"),
            "user_id": data.get("user_id")
        }

    def get_data(self, *args, **kwargs):
        params = self.get_request_params(*args, **kwargs)

        # Validate alert_id
        if not params.get("alert_id"):
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.ALERT_ID_REQUIRED_MESSAGE}

        # Get alert
        try:
            alert = Alert.objects.get(id=params.get("alert_id"))
        except Alert.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_404_NOT_FOUND)
            return {"message": GenericConstants.ALERT_NOT_FOUND_MESSAGE}

        # Check if already archived
        if alert.is_archived:
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.ALERT_ALREADY_ARCHIVED_MESSAGE}

        # Store old values for audit log
        old_values = {
            "is_archived": alert.is_archived
        }

        # Archive the alert
        alert.is_archived = True
        alert.save()

        # Create audit log
        Commons.create_audit_log(
            user_id=params.get("user_id"),
            action="update",
            resource_type="Alert",
            resource_id=alert.id,
            old_values=old_values,
            new_values={
                "is_archived": True,
                "title": alert.title,
                "severity": alert.severity
            }
        )

        self.set_status_code(status_code=status.HTTP_200_OK)
        return {
            "message": GenericConstants.ALERT_ARCHIVED_SUCCESSFUL_MESSAGE,
        }