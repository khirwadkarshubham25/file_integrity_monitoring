from rest_framework import status

from monitoring.models import Baseline
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper
from file_integrity_monitoring.commons.generic_constants import GenericConstants
from file_integrity_monitoring.commons.commons import Commons


class DeleteBaselineService(MonitoringServiceHelper):
    """Service to delete a baseline"""

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        """Extract and validate baseline deletion parameters"""
        data = kwargs.get("data")
        return {
            "baseline_id": data.get("baseline_id"),
            "user_id": data.get("user_id")
        }

    def get_data(self, *args, **kwargs):
        params = self.get_request_params(*args, **kwargs)

        if not params.get("baseline_id"):
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.BASELINE_ID_REQUIRED_MESSAGE}

        try:
            baseline = Baseline.objects.get(id=params.get("baseline_id"))
        except Baseline.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_404_NOT_FOUND)
            return {"message": GenericConstants.BASELINE_NOT_FOUND_MESSAGE}

        baseline_id = baseline.id
        baseline_name = baseline.name

        baseline.delete()

        Commons.create_audit_log(
            user_id=params.get("user_id"),
            action="delete",
            resource_type="Baseline",
            resource_id=baseline_id,
            old_values={
                "id": baseline_id,
                "name": baseline_name
            }
        )

        self.set_status_code(status_code=status.HTTP_200_OK)
        return {
            "message": GenericConstants.BASELINE_DELETE_SUCCESSFUL_MESSAGE,
        }