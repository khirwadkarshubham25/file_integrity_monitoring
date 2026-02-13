from rest_framework import status

from monitoring.models import Alert
from accounts.models import Users
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper
from file_integrity_monitoring.commons.generic_constants import GenericConstants
from file_integrity_monitoring.commons.commons import Commons


class AlertMarkReadCreateService(MonitoringServiceHelper):
    """Service to mark an alert as read by a user"""

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        """Extract and validate alert read parameters"""
        data = kwargs.get("data")
        return {
            "alert_id": data.get("alert_id"),
            "user_id": data.get("user_id")
        }

    def get_data(self, *args, **kwargs):
        """Mark alert as read and return response"""
        params = self.get_request_params(*args, **kwargs)

        # Validate alert_id
        if not params.get("alert_id"):
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.ALERT_ID_REQUIRED_MESSAGE}

        # Validate user_id
        if not params.get("user_id"):
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.USER_ID_REQUIRED_MESSAGE}

        # Get alert
        try:
            alert = Alert.objects.get(id=params.get("alert_id"))
        except Alert.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_404_NOT_FOUND)
            return {"message": GenericConstants.ALERT_NOT_FOUND_MESSAGE}

        # Check if user exists
        try:
            user = Users.objects.get(id=params.get("user_id"))
        except Users.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.USER_NOT_FOUND_MESSAGE}

        # Store old values for audit log
        old_values = {
            "read": alert.read
        }

        # Mark alert as read and add user to M2M
        alert.mark_as_read(user)

        # Create audit log
        Commons.create_audit_log(
            user_id=params.get("read_by"),
            action="update",
            resource_type="Alert",
            resource_id=alert.id,
            old_values=old_values,
            new_values={
                "read": True,
                "title": alert.title,
                "severity": alert.severity
            }
        )

        self.set_status_code(status_code=status.HTTP_200_OK)
        return {
            "message": GenericConstants.ALERT_MARK_READ_SUCCESSFUL_MESSAGE
        }