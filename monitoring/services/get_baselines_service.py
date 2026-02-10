from monitoring.models import Baseline
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper


class GetBaselinesService(MonitoringServiceHelper):

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        data = kwargs.get("data")
        return {
            "page": int(data.get("page", 1)),
            "page_size": int(data.get("page_size", 10)),
            "sort_by": data.get("sort_by", "created_at"),
            "sort_order": data.get("sort_order", "desc"),
            "status": data.get("status")
        }

    def get_data(self, *args, **kwargs):
        params = self.get_request_params(*args, **kwargs)

        queryset = Baseline.objects.all()

        if params.get("status"):
            queryset = queryset.filter(status=params.get("status"))

        sort_by = params.get("sort_by")
        if params.get("sort_order") == "desc":
            sort_by = f"-{sort_by}"

        queryset = queryset.order_by(sort_by)

        page = params.get("page")
        page_size = params.get("page_size")
        start = (page - 1) * page_size
        end = start + page_size

        paginated_baselines = queryset[start:end]

        baselines_data = []
        for baseline in paginated_baselines:
            baseline_dict = {
                "id": baseline.id,
                "name": baseline.name,
                "path": baseline.path,
                "algorithm_type": baseline.algorithm_type,
                "monitoring_enabled": baseline.monitoring_enabled,
                "file_count": baseline.file_count(),
                "recent_changes_count": baseline.recent_changes_count(),
                "created_at": baseline.created_at,
            }
            baselines_data.append(baseline_dict)

        return {
            "baselines": baselines_data,
            "total": queryset.count(),
            "page": page,
            "page_size": page_size
        }