from rest_framework import status

from monitoring.models import Alert
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper
from file_integrity_monitoring.commons.generic_constants import GenericConstants


class GetAlertDetailsService(MonitoringServiceHelper):

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        """Extract and validate alert ID parameter"""
        data = kwargs.get("data")
        return {
            "alert_id": data.get("alert_id")
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

        # Serialize complete alert data
        alert_dict = {
            "id": alert.id,
            "file_change_id": alert.file_change.id,
            "severity": alert.severity,
            "title": alert.title,
            "message": alert.message,
            "file_path": alert.file_path,
            "change_type": alert.change_type,
            "created_at": alert.created_at.isoformat(),
            "updated_at": alert.updated_at.isoformat(),
            "sent_at": alert.sent_at.isoformat() if alert.sent_at else None,
            "read": alert.read,
            "is_archived": alert.is_archived,
            "alert_channels": alert.alert_channels,
            "metadata": alert.metadata
        }

        self.set_status_code(status_code=status.HTTP_200_OK)
        return {
            "alert": alert_dict
        }