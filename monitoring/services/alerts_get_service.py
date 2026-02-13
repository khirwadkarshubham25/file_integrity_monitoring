from rest_framework import status

from monitoring.models import Alert
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper


class AlertsGetService(MonitoringServiceHelper):
    """
    Get Alerts Service
    """
    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        """
        Get Request Params
        @params args: request params
        @params kwargs: request params
        @return request params
        """
        data = kwargs.get("data")
        return {
            "page": int(data.get("page", 1)),
            "page_size": int(data.get("page_size", 10)),
            "sort_by": data.get("sort_by", "created_at"),
            "sort_order": data.get("sort_order", "desc"),
            "severity": data.get("severity"),
            "read": data.get("read"),
            "is_archived": data.get("is_archived")
        }

    def get_data(self, *args, **kwargs):
        """
        Get Alerts Data
        @params args: request params
        @params kwargs: request params
        @return request params
        """
        params = self.get_request_params(*args, **kwargs)

        # Start with all alerts
        queryset = Alert.objects.all()

        # Apply severity filter if provided
        if params.get("severity"):
            queryset = queryset.filter(severity=params.get("severity"))

        # Apply read filter if provided
        if params.get("read") is not None:
            read_value = params.get("read").lower() in ['true', '1', 'yes']
            queryset = queryset.filter(read=read_value)

        # Apply is_archived filter if provided
        if params.get("is_archived") is not None:
            is_archived_value = params.get("is_archived").lower() in ['true', '1', 'yes']
            queryset = queryset.filter(is_archived=is_archived_value)

        # Apply sorting
        sort_by = params.get("sort_by")
        if params.get("sort_order") == "desc":
            sort_by = f"-{sort_by}"

        queryset = queryset.order_by(sort_by)

        # Apply pagination
        page = params.get("page")
        page_size = params.get("page_size")
        start = (page - 1) * page_size
        end = start + page_size

        paginated_alerts = queryset[start:end]

        # Serialize alerts data
        alerts_data = []
        for alert in paginated_alerts:
            alert_dict = {
                "alert_id": alert.id,
                "title": alert.title,
                "severity": alert.severity,
                "file_path": alert.file_path,
                "change_type": alert.change_type,
                "created_at": alert.created_at.isoformat(),
                "read": alert.read,
                "is_archived": alert.is_archived
            }
            alerts_data.append(alert_dict)

        self.set_status_code(status_code=status.HTTP_200_OK)
        return {
            "alerts": alerts_data,
            "total": queryset.count(),
            "page": page,
            "page_size": page_size
        }