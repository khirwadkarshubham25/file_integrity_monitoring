from django.db.models import Q
from rest_framework import status

from monitoring.models import WhitelistRule
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper


class GetWhitelistRulesService(MonitoringServiceHelper):
    """Service to get whitelist rules with pagination and filtering"""

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        """Extract whitelist rules parameters"""
        data = kwargs.get("data")
        return {
            "page": data.get("page", "1"),
            "page_size": data.get("page_size", "10"),
            "baseline_id": data.get("baseline_id"),
            "active": data.get("active")
        }

    def get_data(self, *args, **kwargs):
        """Get whitelist rules with filtering"""
        params = self.get_request_params(*args, **kwargs)

        try:
            # Build query filters
            filters = Q()

            if params.get("baseline_id"):
                filters &= Q(baseline_id=params.get("baseline_id"))

            if params.get("active") is not None:
                active = params.get("active")
                if isinstance(active, str):
                    active = active.lower() == 'true'
                filters &= Q(active=active)

            # Get total count
            total_count = WhitelistRule.objects.filter(filters).count()

            # Get paginated results
            page = int(params.get("page", 1))
            page_size = int(params.get("page_size", 10))
            start = (page - 1) * page_size
            end = start + page_size

            whitelist_rules = WhitelistRule.objects.filter(filters)[start:end]

            # Build response
            rules_data = []
            for rule in whitelist_rules:
                rules_data.append({
                    'id': rule.id,
                    'baseline_id': rule.baseline.id,
                    'baseline_name': rule.baseline.name,
                    'file_pattern': rule.file_pattern,
                    'change_types': rule.change_types,
                    'reason': rule.reason,
                    'active': rule.active,
                    'user_id': rule.user.id,
                    'created_at': rule.created_at.isoformat() if rule.created_at else None,
                    'updated_at': rule.updated_at.isoformat() if rule.updated_at else None,
                    'expires_at': rule.expires_at.isoformat() if rule.expires_at else None,
                })

            # Calculate pagination info
            total_pages = (total_count + page_size - 1) // page_size

            self.set_status_code(status_code=status.HTTP_200_OK)
            return {
                "total_count": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "rules": rules_data
            }

        except Exception as e:
            self.error = True
            self.set_status_code(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return {"message": f"Error retrieving whitelist rules: {str(e)}"}