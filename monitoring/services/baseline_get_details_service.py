from rest_framework import status

from monitoring.models import Baseline
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper
from file_integrity_monitoring.commons.generic_constants import GenericConstants


class BaselineGetDetailsService(MonitoringServiceHelper):
    """
    Baseline details service
    """
    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        """
        Get request params
        @param args: request params
        @param kwargs: request params
        """
        data = kwargs.get("data")
        return {
            "baseline_id": data.get("baseline_id")
        }

    def get_data(self, *args, **kwargs):
        """
        Get Baseline details
        @param args: request params
        @param kwargs: request params
        @return response data
        """
        params = self.get_request_params(*args, **kwargs)

        if not params.get("baseline_id"):
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.BASELINE_ID_REQUIRED_MESSAGE}

        try:
            baseline = Baseline.objects.get(id=params.get("baseline_id"))
        except Baseline.DoesNotExist:
            self.set_status_code(status_code=status.HTTP_404_NOT_FOUND)
            return {"message": GenericConstants.BASELINE_NOT_FOUND_MESSAGE}

        baseline_dict = {
            "id": baseline.id,
            "name": baseline.name,
            "description": baseline.description,
            "path": baseline.path,
            "version": baseline.version,
            "status": baseline.status,
            "user_id": baseline.user.id,
            "created_at": baseline.created_at.isoformat(),
            "updated_at": baseline.updated_at.isoformat(),
            "is_active": baseline.is_active,
            "monitoring_enabled": baseline.monitoring_enabled,
            "algorithm_type": baseline.algorithm_type,
            "exclude_patterns": baseline.exclude_patterns,
            "file_count": baseline.file_count(),
        }

        self.set_status_code(status_code=status.HTTP_200_OK)
        return {
            "baseline": baseline_dict
        }