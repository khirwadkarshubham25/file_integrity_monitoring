from rest_framework import status

from monitoring.models import MonitoringSession
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper
from file_integrity_monitoring.commons.generic_constants import GenericConstants


class GetMonitoringSessionDetailsService(MonitoringServiceHelper):
    """Service to retrieve complete monitoring session details by ID"""

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        """Extract and validate session ID parameter"""
        data = kwargs.get("data")
        return {
            "session_id": data.get("session_id")
        }

    def get_data(self, *args, **kwargs):
        """Fetch complete monitoring session details and return response"""
        params = self.get_request_params(*args, **kwargs)

        # Validate session_id
        if not params.get("session_id"):
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.SESSION_ID_REQUIRED_MESSAGE}

        # Get monitoring session
        try:
            session = MonitoringSession.objects.get(id=params.get("session_id"))
        except MonitoringSession.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_404_NOT_FOUND)
            return {"message": GenericConstants.MONITORING_SESSION_NOT_FOUND_MESSAGE}

        # Serialize complete monitoring session data
        session_dict = {
            "id": session.id,
            "baseline_id": session.baseline.id,
            "monitor_type": session.monitor_type,
            "baseline_name": session.baseline.name,
            "baseline_path": session.baseline.path,
            "status": session.status,
            "start_time": session.start_time.isoformat() if session.start_time else None,
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "duration_seconds": session.duration_seconds(),
            "files_scanned": session.files_scanned,
            "files_changed": session.files_changed,
            "files_critical": session.files_critical,
            "files_added": session.files_added,
            "files_deleted": session.files_deleted,
            "error_message": session.error_message,
            "user_id": session.user.id if session.user else None,
            "user_name": session.user.email if session.user else None,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "metadata": session.metadata
        }

        return {
            "monitoring_session": session_dict
        }