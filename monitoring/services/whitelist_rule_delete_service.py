from rest_framework import status

from file_integrity_monitoring.commons.generic_constants import GenericConstants
from monitoring.models import WhitelistRule
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper
from file_integrity_monitoring.commons.commons import Commons


class WhitelistRuleDeleteService(MonitoringServiceHelper):
    """Service to delete a whitelist rule"""

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        """Extract whitelist rule parameters"""
        data = kwargs.get("data")
        return {
            "rule_id": data.get("rule_id"),
            "user_id": data.get("user_id")
        }

    def get_data(self, *args, **kwargs):
        """Delete whitelist rule"""
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
            # Store values for audit log before deletion
            rule_id = whitelist_rule.id
            baseline_id = whitelist_rule.baseline.id
            file_pattern = whitelist_rule.file_pattern

            old_values = {
                "baseline_id": baseline_id,
                "file_pattern": file_pattern,
                "change_types": whitelist_rule.change_types,
                "reason": whitelist_rule.reason,
                "active": whitelist_rule.active
            }

            # Delete the rule
            whitelist_rule.delete()

            # Create audit log
            Commons.create_audit_log(
                user_id=params.get("user_id"),
                action="delete",
                resource_type="WhitelistRule",
                resource_id=rule_id,
                old_values=old_values
            )

            self.set_status_code(status_code=status.HTTP_200_OK)
            return {
                "message": GenericConstants.WHITELIST_RULE_DELETE_SUCCESSFUL_MESSAGE,
            }

        except Exception as e:
            self.error = True
            self.set_status_code(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return {"message": f"Error deleting whitelist rule: {str(e)}"}