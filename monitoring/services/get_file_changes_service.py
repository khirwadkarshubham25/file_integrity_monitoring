from rest_framework import status

from monitoring.models import FileChange, Baseline
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper
from file_integrity_monitoring.commons.generic_constants import GenericConstants


class GetFileChangesService(MonitoringServiceHelper):
    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        data = kwargs.get("data")
        return {
            "baseline_id": data.get("baseline_id"),
            "page": int(data.get("page", 1)),
            "page_size": int(data.get("page_size", 10)),
            "sort_by": data.get("sort_by", "detected_at"),
            "sort_order": data.get("sort_order", "desc"),
            "severity": data.get("severity"),
            "change_type": data.get("change_type"),
            "acknowledged": data.get("acknowledged")
        }

    def get_data(self, *args, **kwargs):
        params = self.get_request_params(*args, **kwargs)

        queryset = FileChange.objects.all()

        if params.get("baseline_id"):
            try:
                baseline = Baseline.objects.get(id=params.get("baseline_id"))
                queryset = queryset.filter(baseline=baseline)
            except Baseline.DoesNotExist:
                self.error = True
                self.set_status_code(status_code=status.HTTP_404_NOT_FOUND)
                return {"message": GenericConstants.BASELINE_NOT_FOUND_MESSAGE}

        if params.get("severity"):
            queryset = queryset.filter(severity=params.get("severity"))

        if params.get("change_type"):
            queryset = queryset.filter(change_type=params.get("change_type"))

        if params.get("acknowledged") is not None:
            acknowledged_value = params.get("acknowledged").lower() in ['true', '1', 'yes']
            queryset = queryset.filter(acknowledged=acknowledged_value)

        sort_by = params.get("sort_by")
        if params.get("sort_order") == "desc":
            sort_by = f"-{sort_by}"

        queryset = queryset.order_by(sort_by)

        page = params.get("page")
        page_size = params.get("page_size")
        start = (page - 1) * page_size
        end = start + page_size

        paginated_changes = queryset[start:end]

        changes_data = []
        for change in paginated_changes:
            change_dict = {
                "id": change.id,
                "file_path": change.file_path,
                "change_type": change.change_type,
                "severity": change.severity,
                "detected_at": change.detected_at.isoformat(),
                "acknowledged": change.acknowledged,
                "expected": change.expected
            }
            changes_data.append(change_dict)

        return {
            "changes": changes_data,
            "total": queryset.count(),
            "page": page,
            "page_size": page_size,
            "baseline_id": params.get("baseline_id")
        }