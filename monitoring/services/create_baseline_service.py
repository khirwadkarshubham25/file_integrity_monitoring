import os
import threading

from rest_framework import status

from accounts.models import Users
from file_integrity_monitoring.commons.commons import Commons
from file_integrity_monitoring.commons.generic_constants import GenericConstants
from monitoring.models import Baseline
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper


class CreateBaselineService(MonitoringServiceHelper):

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        """Extract and validate baseline creation parameters"""
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
        """Create baseline and optionally scan files"""
        params = self.get_request_params(*args, **kwargs)

        # Validate required fields
        if not params.get("name"):
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": "Baseline name is required"}

        if not params.get("path"):
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": "Path is required"}

        # Check if baseline with same name already exists
        if Baseline.objects.filter(name=params.get("name")).exists():
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": "Baseline with this name already exists"}

        # Validate path exists
        if not os.path.isdir(params.get("path")):
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": f"Path does not exist: {params.get('path')}"}

        # Get user
        try:
            user = Users.objects.get(id=params.get("user_id"))
        except Users.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": "User not found"}

        # Create baseline with "scanning" status
        baseline = Baseline.objects.create(
            name=params.get("name"),
            description=params.get("description"),
            path=params.get("path"),
            algorithm_type=params.get("algorithm_type"),
            exclude_patterns=params.get("exclude_patterns"),
            monitoring_enabled=params.get("monitoring_enabled"),
            user=user,
            status="scanning"
        )

        # Count files to determine approach
        file_count = self.count_files(params.get("path"), params.get("exclude_patterns"))

        if file_count < GenericConstants.SYNC_FILE_THRESHOLD:
            try:
                self.scan_baseline_files_sync(baseline, params)
                baseline.status = "ready"
                baseline.save()

                self.set_status_code(status_code=status.HTTP_201_CREATED)
                return {
                    "message": "Baseline created and scanned successfully",
                    "baseline_id": baseline.id,
                    "name": baseline.name,
                    "path": baseline.path,
                    "status": "ready",
                    "file_count": baseline.baseline_files.count(),
                    "scanning": False
                }
            except Exception as e:
                baseline.status = "error"
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

            self.set_status_code(status_code=status.HTTP_202_ACCEPTED)
            return {
                "message": "Baseline created. File scanning in progress...",
                "baseline_id": baseline.id,
                "name": baseline.name,
                "path": baseline.path,
                "status": "scanning",
                "file_count": 0,
                "scanning": True,
                "estimated_files": file_count
            }



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