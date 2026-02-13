from rest_framework import status

from monitoring.models import MonitoringSession
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper


class MonitoringSessionsGetService(MonitoringServiceHelper):
    """
    Service to retrieve monitoring sessions with pagination, sorting, and filtering
    """

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        """
        Extract pagination, sorting, and filtering parameters
        @params args: positional parameters
        @params kwargs: keyword parameters
        """
        data = kwargs.get("data")
        return {
            "page": int(data.get("page", 1)),
            "page_size": int(data.get("page_size", 10)),
            "sort_by": data.get("sort_by", "created_at"),
            "sort_order": data.get("sort_order", "desc"),
            "status": data.get("status"),
            "baseline_id": data.get("baseline_id")
        }

    def get_data(self, *args, **kwargs):
        """
        Fetch monitoring sessions with pagination and filtering
        @params args: positional parameters
        @params kwargs: keyword parameters
        """
        params = self.get_request_params(*args, **kwargs)

        queryset = MonitoringSession.objects.all()
        if params.get("baseline_id"):
            queryset = queryset.filter(baseline_id=params.get("baseline_id"))

        if params.get("status"):
            queryset = queryset.filter(status=params.get("status"))

        sort_by = params.get("sort_by")
        if params.get("sort_order") == "desc":
            sort_by = f"-{sort_by}"

        queryset = queryset.order_by(sort_by)

        # Apply pagination
        page = params.get("page")
        page_size = params.get("page_size")
        start = (page - 1) * page_size
        end = start + page_size

        paginated_sessions = queryset[start:end]

        # Serialize sessions data
        sessions_data = []
        for session in paginated_sessions:
            session_dict = {
                "monitor_session_id": session.id,
                "baseline_id": session.baseline.id,
                "baseline_name": session.baseline.name,
                "monitor_type": session.monitor_type,
                "status": session.status,
                "start_time": session.start_time.isoformat() if session.start_time else None,
                "end_time": session.end_time.isoformat() if session.end_time else None,
            }
            sessions_data.append(session_dict)

        self.set_status_code(status_code=status.HTTP_200_OK)
        return {
            "monitoring_sessions": sessions_data,
            "total": queryset.count(),
            "page": page,
            "page_size": page_size
        }