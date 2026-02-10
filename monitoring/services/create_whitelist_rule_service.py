from rest_framework import status

from file_integrity_monitoring.commons.generic_constants import GenericConstants
from monitoring.models import WhitelistRule, Baseline, Users
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper
from file_integrity_monitoring.commons.commons import Commons


class CreateWhitelistRuleService(MonitoringServiceHelper):
    """Service to create a new whitelist rule"""

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        """Extract whitelist rule parameters"""
        data = kwargs.get("data")
        return {
            "baseline_id": data.get("baseline_id"),
            "file_pattern": data.get("file_pattern"),
            "change_types": data.get("change_types", []),
            "reason": data.get("reason", ""),
            "active": data.get("active", True),
            "user_id": data.get("user_id"),
            "expires_at": data.get("expires_at")
        }

    def get_data(self, *args, **kwargs):
        """Create new whitelist rule"""
        params = self.get_request_params(*args, **kwargs)

        # Validate required fields
        if not params.get("baseline_id"):
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.BASELINE_ID_REQUIRED_MESSAGE}

        if not params.get("file_pattern"):
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.FILE_PATTERN_REQUIRED_MESSAGE}

        # Get baseline
        try:
            baseline = Baseline.objects.get(id=params.get("baseline_id"))
        except Baseline.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_404_NOT_FOUND)
            return {"message": GenericConstants.BASELINE_NOT_FOUND_MESSAGE}

        # Get or create default user
        try:
            if params.get("user_id"):
                user = Users.objects.get(id=params.get("user_id"))
            else:
                # Create default system user if needed
                user = Users.objects.first()
                if not user:
                    user = Users.objects.create(username='system', email='system@local')
        except Users.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_404_NOT_FOUND)
            return {"message": GenericConstants.USER_NOT_FOUND_MESSAGE}

        try:
            # Create whitelist rule
            whitelist_rule = WhitelistRule.objects.create(
                baseline=baseline,
                file_pattern=params.get("file_pattern"),
                change_types=params.get("change_types", []),
                reason=params.get("reason", ""),
                active=params.get("active", True),
                user=user,
                expires_at=params.get("expires_at")
            )

            # Create audit log
            Commons.create_audit_log(
                user_id=params.get("user_id"),
                action="create",
                resource_type="WhitelistRule",
                resource_id=whitelist_rule.id,
                new_values={
                    "baseline_id": baseline.id,
                    "file_pattern": params.get("file_pattern"),
                    "change_types": params.get("change_types", []),
                    "active": params.get("active", True)
                }
            )

            self.set_status_code(status_code=status.HTTP_201_CREATED)
            return {
                "message": GenericConstants.WHITELIST_RULE_CREATE_SUCCESSFUL_MESSAGE
            }

        except Exception as e:
            self.error = True
            self.set_status_code(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return {"message": f"Error creating whitelist rule: {str(e)}"}