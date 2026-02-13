from rest_framework import status

from monitoring.models import FileChange
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper
from file_integrity_monitoring.commons.generic_constants import GenericConstants


class FileChangeDetailsGetService(MonitoringServiceHelper):
    """
    Get File Change Details
    """
    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        """
        Get Request Parameters
        """
        data = kwargs.get("data")
        return {
            "change_id": data.get("change_id")
        }

    def get_data(self, *args, **kwargs):
        """
        File change details get data
        """
        params = self.get_request_params(*args, **kwargs)

        # Validate change_id
        if not params.get("change_id"):
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.FILE_CHANGE_ID_REQUIRED_MESSAGE}

        try:
            change = FileChange.objects.get(id=params.get("change_id"))
        except FileChange.DoesNotExist:
            self.set_status_code(status_code=status.HTTP_404_NOT_FOUND)
            return {"message": GenericConstants.FILE_CHANGE_NOT_FOUND_MESSAGE}

        change_dict = {
            "change_id": change.id,
            "baseline_id": change.baseline.id,
            "baseline_name": change.baseline.name,
            "baseline_file_id": change.baseline_file.id if change.baseline_file else None,
            "file_path": change.file_path,
            "current_hash": change.current_hash,
            "change_type": change.change_type,
            "severity": change.severity,
            "change_details": change.change_details,
            "detected_at": change.detected_at.isoformat(),
            "created_at": change.created_at.isoformat() if change.created_at else None,
            "updated_at": change.updated_at.isoformat(),
            "acknowledged": change.acknowledged,
            "user_id": change.user.id if change.user else None,
            "user_name": change.user.email if change.user else None,
            "acknowledged_reason": change.acknowledged_reason,
            "expected": change.expected,
            "metadata": change.metadata
        }

        return {
            "change": change_dict
        }