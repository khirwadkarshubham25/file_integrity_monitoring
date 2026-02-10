from rest_framework import status
import os

from monitoring.models import Alert, FileChange
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper
from file_integrity_monitoring.commons.generic_constants import GenericConstants
from file_integrity_monitoring.commons.commons import Commons


class CreateAlertService(MonitoringServiceHelper):
    """Service to create alerts from file changes"""

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        """Extract and validate alert creation parameters"""
        data = kwargs.get("data")
        return {
            "change_id": data.get("change_id"),
            "user_id": data.get("user_id")
        }

    def get_data(self, *args, **kwargs):
        """Create alert from file change and return response"""
        params = self.get_request_params(*args, **kwargs)

        # Validate change_id
        if not params.get("change_id"):
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.FILE_CHANGE_ID_REQUIRED_MESSAGE}

        # Get file change
        try:
            change = FileChange.objects.get(id=params.get("change_id"))
        except FileChange.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_404_NOT_FOUND)
            return {"message": GenericConstants.FILE_CHANGE_NOT_FOUND_MESSAGE}

        # Check if alert already exists for this change
        if Alert.objects.filter(file_change_id=change.id).exists():
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.ALERT_ALREADY_EXISTS}

        # Generate title and message
        title = self._generate_title(change)
        message = self._generate_message(change)

        # Create alert
        alert = Alert(
            file_change_id=change.id,
            severity=change.severity,
            title=title,
            message=message,
            file_path=change.file_path,
            change_type=change.change_type,
            alert_channels=['in_app'],
            read=False,
            is_archived=False,
            metadata={
                'baseline_id': change.baseline.id,
                'detection_method': 'auto_scan'
            }
        )
        alert.save()

        # Create audit log
        Commons.create_audit_log(
            user_id=params.get("user_id"),
            action="create",
            resource_type="Alert",
            resource_id=alert.id,
            new_values={
                "file_change_id": change.id,
                "severity": change.severity,
                "title": title,
                "file_path": change.file_path,
                "change_type": change.change_type
            }
        )

        self.set_status_code(status_code=status.HTTP_201_CREATED)
        return {
            "message": "Alert created successfully",
        }

    def _generate_title(self, change):
        """Generate alert title from change details"""
        # Extract filename from path
        filename = os.path.basename(change.file_path)

        # Format severity label (capitalize)
        severity_label = change.severity.upper()

        # Format change type label (replace underscores with spaces, capitalize)
        change_type_label = change.change_type.replace('_', ' ').title()

        return f"[{severity_label}] {change_type_label}: {filename}"

    def _generate_message(self, change):
        """Generate alert message from change details"""
        baseline_name = change.baseline.name
        detected_time = change.detected_at.strftime("%Y-%m-%d %H:%M:%S UTC")

        # Create severity description
        severity_descriptions = {
            'critical': 'Critical file change detected',
            'high': 'High priority file change detected',
            'medium': 'File change detected',
            'low': 'Low priority file change detected',
            'info': 'File change information'
        }

        description = severity_descriptions.get(change.severity, 'File change detected')

        # Build message
        message = f"{description}: {change.file_path}\n"
        message += f"Baseline: {baseline_name}\n"
        message += f"Change Type: {change.change_type.replace('_', ' ').title()}\n"
        message += f"Detected: {detected_time}\n"
        message += f"Severity: {change.severity.upper()}"

        return message