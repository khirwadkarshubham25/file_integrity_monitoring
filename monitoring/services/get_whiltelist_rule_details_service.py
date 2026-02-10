from rest_framework import status

from file_integrity_monitoring.commons.generic_constants import GenericConstants
from monitoring.models import WhitelistRule
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper


class GetWhitelistRuleDetailsService(MonitoringServiceHelper):
    """Service to retrieve complete whitelist rule details by ID"""

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        """Extract and validate whitelist rule ID parameter"""
        data = kwargs.get("data")
        return {
            "rule_id": data.get("rule_id")
        }

    def get_data(self, *args, **kwargs):
        """Fetch complete whitelist rule details and return response"""
        params = self.get_request_params(*args, **kwargs)

        # Validate rule_id
        if not params.get("rule_id"):
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.WHITELIST_RULE_ID_REQUIRED_MESSAGE}

        # Get whitelist rule
        try:
            rule = WhitelistRule.objects.get(id=params.get("rule_id"))
        except WhitelistRule.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_404_NOT_FOUND)
            return {"message": GenericConstants.WHITELIST_RULE_NOT_FOUND_MESSAGE}

        # Serialize complete whitelist rule data
        rule_dict = {
            "id": rule.id,
            "baseline_id": rule.baseline.id,
            "baseline_name": rule.baseline.name if rule.baseline else None,
            "file_pattern": rule.file_pattern,
            "change_types": rule.change_types,
            "reason": rule.reason,
            "description": rule.description if hasattr(rule, 'description') else None,
            "active": rule.active,
            "user_id": rule.user.id,
            "created_at": rule.created_at.isoformat() if rule.created_at else None,
            "updated_at": rule.updated_at.isoformat() if rule.updated_at else None,
            "expires_at": rule.expires_at.isoformat() if rule.expires_at else None,
            "priority": rule.priority if hasattr(rule, 'priority') else None,
            "metadata": rule.metadata if hasattr(rule, 'metadata') else None,
            "is_expired": self._is_rule_expired(rule),
            "days_until_expiry": self._get_days_until_expiry(rule)
        }

        self.set_status_code(status_code=status.HTTP_200_OK)
        return {
            "whitelist_rule": rule_dict
        }

    def _is_rule_expired(self, rule):
        """Check if whitelist rule has expired"""
        if not rule.expires_at:
            return False
        from datetime import datetime
        from django.utils import timezone
        return timezone.now() > rule.expires_at

    def _get_days_until_expiry(self, rule):
        """Calculate days remaining until rule expires"""
        if not rule.expires_at:
            return None
        from datetime import datetime
        from django.utils import timezone
        now = timezone.now()
        if now > rule.expires_at:
            return 0
        delta = rule.expires_at - now
        return delta.days