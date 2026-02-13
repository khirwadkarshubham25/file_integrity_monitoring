import os
import threading

from rest_framework import status

from accounts.models import Users
from file_integrity_monitoring.commons.commons import Commons
from file_integrity_monitoring.commons.generic_constants import GenericConstants
from monitoring.models import Baseline
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper


class BaselineCreateService(MonitoringServiceHelper):
    """
        Create baseline and scan files
    """
    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        """
        Extract and validate baseline creation parameters
        @param: *args
        @param: **kwargs
        @return Dictionary of request parameters
        """
        data = kwargs.get("data")
        return {
            "name": data.get("name"),
            "description": data.get("description", ""),
            "path": data.get("path"),
            "algorithm_type": data.get("algorithm_type", "sha256"),
            "exclude_patterns": data.get("exclude_patterns", []),
            "monitoring_enabled": data.get("monitoring_enabled", True),
            "user_id": data.get("user_id") or data.get("created_by")
        }

    def get_data(self, *args, **kwargs):
        """
        Create baseline and scan files
        @param: *args
        @param: **kwargs
        @return Response
        """
        params = self.get_request_params(*args, **kwargs)

        if not params.get("name"):
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.BASELINE_NAME_REQUIRED_MESSAGE}

        if not params.get("path"):
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.BASELINE_PATH_REQUIRED_MESSAGE}

        if Baseline.objects.filter(name=params.get("name")).exists():
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.BASELINE_NAME_ALREADY_EXISTS_MESSAGE}

        # Validate path exists
        if not os.path.isdir(params.get("path")):
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.BASELINE_PATH_DOES_NOT_EXIST.format(params.get('path'))}

        try:
            user = Users.objects.get(id=params.get("user_id"))
        except Users.DoesNotExist:
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.USER_NOT_FOUND_MESSAGE}

        baseline = Baseline.objects.create(
            name=params.get("name"),
            description=params.get("description"),
            path=params.get("path"),
            algorithm_type=params.get("algorithm_type"),
            exclude_patterns=params.get("exclude_patterns"),
            monitoring_enabled=params.get("monitoring_enabled"),
            user=user,
            status=GenericConstants.STATUS_SCANNING
        )

        # Count files to determine approach
        is_success, file_count = self.count_files(params.get("path"), params.get("exclude_patterns"))

        if not is_success:
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.BASELINE_FILES_COUNT_ERROR_MESSAGE}

        if file_count < GenericConstants.SYNC_FILE_THRESHOLD:
            try:
                is_success, message = self.scan_baseline_files_sync(baseline, params)
                if not is_success:
                    return {"message": message}

                baseline.status = GenericConstants.STATUS_ACTIVE
                baseline.save()

                Commons.create_audit_log(
                    user_id=params.get("user_id"),
                    action=GenericConstants.ACTION_CREATE,
                    resource_type=GenericConstants.RESOURCE_TYPE_BASELINE,
                    resource_id=baseline.id,
                    new_values={
                        "name": baseline.name,
                        "path": baseline.path,
                    }
                )

                return {
                    "message": GenericConstants.BASELINE_CREATE_SUCCESSFUL_MESSAGE
                }
            except Exception as e:
                baseline.status = GenericConstants.STATUS_ERROR
                baseline.save()
                self.error = True
                self.set_status_code(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return {"message": f"Error scanning baseline: {str(e)}"}
        else:
            thread = threading.Thread(
                target=self._scan_baseline_files_async,
                args=(baseline.id, params),
                daemon=True
            )
            thread.start()

            return {
                "message": GenericConstants.BASELINE_CREATE_SUCCESSFUL_MESSAGE
            }


    # TODO - Future Scope
    def _scan_baseline_files_async(self, baseline_id, params):
        """Asynchronously scan directory (>= 5000 files) - runs in background thread"""
        try:
            baseline = Baseline.objects.get(id=baseline_id)

            # Perform same scan as sync version
            self.scan_baseline_files_sync(baseline, params)

            # Update status to ready
            baseline.status = "ready"
            baseline.save()

            # Create audit log for completion
            Commons.create_audit_log(
                user_id=params.get("user_id"),
                action="scan_complete",
                resource_type="Baseline",
                resource_id=baseline_id,
                new_values={
                    "status": "ready",
                    "file_count": baseline.baseline_files.count()
                }
            )

        except Exception as e:
            print(f"Error in async scan for baseline {baseline_id}: {str(e)}")
            try:
                baseline = Baseline.objects.get(id=baseline_id)
                baseline.status = "error"
                baseline.save()
            except:
                pass