from rest_framework import status

from file_integrity_monitoring.commons.generic_constants import GenericConstants
from monitoring.models import WhitelistRule
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper
from file_integrity_monitoring.commons.commons import Commons


class UpdateWhitelistRuleService(MonitoringServiceHelper):
    """Service to update a whitelist rule"""

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        """Extract whitelist rule parameters"""
        data = kwargs.get("data")
        return {
            "rule_id": data.get("rule_id"),
            "file_pattern": data.get("file_pattern"),
            "change_types": data.get("change_types"),
            "reason": data.get("reason"),
            "active": data.get("active"),
            "user_id": data.get("user_id"),
            "expires_at": data.get("expires_at")
        }

    def get_data(self, *args, **kwargs):
        """Update whitelist rule"""
        params = self.get_request_params(*args, **kwargs)

        # Validate rule_id
        if not params.get("rule_id"):
            self.error = True
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            return {"message": GenericConstants.WHITELIST_RULE_ID_REQUIRED_MESSAGE}

        # Get whitelist rule
        try:
            whitelist_rule = WhitelistRule.objects.get(id=params.get("rule_id"))
        except WhitelistRule.DoesNotExist:
            self.error = True
            self.set_status_code(status_code=status.HTTP_404_NOT_FOUND)
            return {"message": GenericConstants.WHITELIST_RULE_NOT_FOUND_MESSAGE}

        try:
            # Store old values for audit log
            old_values = {
                "file_pattern": whitelist_rule.file_pattern,
                "change_types": whitelist_rule.change_types,
                "reason": whitelist_rule.reason,
                "active": whitelist_rule.active,
                "expires_at": whitelist_rule.expires_at
            }

            # Update fields if provided
            if params.get("file_pattern") is not None:
                whitelist_rule.file_pattern = params.get("file_pattern")

            if params.get("change_types") is not None:
                whitelist_rule.change_types = params.get("change_types")

            if params.get("reason") is not None:
                whitelist_rule.reason = params.get("reason")

            if params.get("active") is not None:
                whitelist_rule.active = params.get("active")

            if params.get("expires_at") is not None:
                whitelist_rule.expires_at = params.get("expires_at")

            whitelist_rule.save()

            # Create audit log
            Commons.create_audit_log(
                user_id=params.get("user_id"),
                action="update",
                resource_type="WhitelistRule",
                resource_id=whitelist_rule.id,
                old_values=old_values,
                new_values={
                    "file_pattern": whitelist_rule.file_pattern,
                    "change_types": whitelist_rule.change_types,
                    "reason": whitelist_rule.reason,
                    "active": whitelist_rule.active,
                    "expires_at": whitelist_rule.expires_at
                }
            )

            self.set_status_code(status_code=status.HTTP_200_OK)
            return {
                "message": GenericConstants.WHITELIST_RULE_UPDATE_SUCCESSFUL_MESSAGE
            }

        except Exception as e:
            self.error = True
            self.set_status_code(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return {"message": f"Error updating whitelist rule: {str(e)}"}