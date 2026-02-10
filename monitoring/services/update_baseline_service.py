from rest_framework import status

from file_integrity_monitoring.commons.commons import Commons
from file_integrity_monitoring.commons.generic_constants import GenericConstants
from monitoring.models import Baseline
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper


class UpdateBaselineService(MonitoringServiceHelper):
    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        data = kwargs.get("data")
        return {
            "baseline_id": data.get("baseline_id"),
            "name": data.get("name"),
            "description": data.get("description"),
            "path": data.get("path"),
            "algorithm_type": data.get("algorithm_type"),
            "exclude_patterns": data.get("exclude_patterns"),
            "monitoring_enabled": data.get("monitoring_enabled"),
            "status": data.get("status"),
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

        old_values = {
            "name": baseline.name,
            "description": baseline.description,
            "path": baseline.path,
            "status": baseline.status,
            "monitoring_enabled": baseline.monitoring_enabled
        }

        if params.get("name"):
            if Baseline.objects.filter(name=params.get("name")).exclude(id=baseline.id).exists():
                self.error = True
                self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
                return {"message": GenericConstants.BASELINE_NAME_ALREADY_EXISTS_MESSAGE}
            baseline.name = params.get("name")

        if params.get("description") is not None:
            baseline.description = params.get("description")

        if params.get("path"):
            baseline.path = params.get("path")

        if params.get("algorithm_type"):
            baseline.algorithm_type = params.get("algorithm_type")

        if params.get("exclude_patterns") is not None:
            baseline.exclude_patterns = params.get("exclude_patterns")

        if params.get("monitoring_enabled") is not None:
            baseline.monitoring_enabled = params.get("monitoring_enabled")

        if params.get("status"):
            baseline.status = params.get("status")

        baseline.save()

        Commons.create_audit_log(
            user_id=params.get("user_id"),
            action="update",
            resource_type="Baseline",
            resource_id=baseline.id,
            old_values=old_values,
            new_values={
                "name": baseline.name,
                "description": baseline.description,
                "path": baseline.path,
                "status": baseline.status,
                "monitoring_enabled": baseline.monitoring_enabled
            }
        )

        self.set_status_code(status_code=status.HTTP_200_OK)
        return {
            "message": GenericConstants.BASELINE_UPDATE_SUCCESSFUL_MESSAGE
        }