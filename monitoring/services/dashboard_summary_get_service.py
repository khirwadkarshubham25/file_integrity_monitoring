from rest_framework import status
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from monitoring.models import (
    MonitoringSession, Baseline, FileChange, Alert, WhitelistRule
)
from monitoring.services.service_helper.monitoring_service_helper import MonitoringServiceHelper


class DashboardSummaryGetService(MonitoringServiceHelper):
    """Service to get dashboard summary statistics"""

    def __init__(self):
        super().__init__()

    def get_request_params(self, *args, **kwargs):
        """Extract dashboard summary parameters"""
        data = kwargs.get("data")
        return {}

    def get_data(self, *args, **kwargs):
        """Get dashboard summary statistics"""
        try:
            # Get current time for time-based queries
            now = timezone.now()
            last_24_hours = now - timedelta(hours=24)
            last_7_days = now - timedelta(days=7)

            # Baseline Statistics
            total_baselines = Baseline.objects.filter(is_active=True).count()
            baselines_monitored = MonitoringSession.objects.filter(
                status='completed'
            ).values('baseline_id').distinct().count()

            # Monitoring Session Statistics
            total_sessions = MonitoringSession.objects.count()
            completed_sessions = MonitoringSession.objects.filter(status='completed').count()
            failed_sessions = MonitoringSession.objects.filter(status='failed').count()
            running_sessions = MonitoringSession.objects.filter(status='running').count()

            sessions_last_24h = MonitoringSession.objects.filter(
                created_at__gte=last_24_hours
            ).count()
            sessions_last_7d = MonitoringSession.objects.filter(
                created_at__gte=last_7_days
            ).count()

            # File Change Statistics
            total_changes = FileChange.objects.count()
            unacknowledged_changes = FileChange.objects.filter(acknowledged=False).count()

            changes_by_severity = {}
            for severity in ['critical', 'high', 'medium', 'low', 'info']:
                count = FileChange.objects.filter(severity=severity).count()
                if count > 0:
                    changes_by_severity[severity] = count

            changes_last_24h = FileChange.objects.filter(
                detected_at__gte=last_24_hours
            ).count()
            changes_last_7d = FileChange.objects.filter(
                detected_at__gte=last_7_days
            ).count()

            # Alert Statistics
            total_alerts = Alert.objects.count()
            unread_alerts = Alert.objects.filter(read=False).count()
            archived_alerts = Alert.objects.filter(is_archived=True).count()
            active_alerts = Alert.objects.filter(read=False, is_archived=False).count()

            alerts_by_severity = {}
            for severity in ['critical', 'high', 'medium', 'low', 'info']:
                count = Alert.objects.filter(severity=severity).count()
                if count > 0:
                    alerts_by_severity[severity] = count

            critical_alerts = Alert.objects.filter(
                severity='critical',
                read=False,
                is_archived=False
            ).count()

            alerts_last_24h = Alert.objects.filter(
                created_at__gte=last_24_hours
            ).count()
            alerts_last_7d = Alert.objects.filter(
                created_at__gte=last_7_days
            ).count()

            # Whitelist Rules Statistics
            total_rules = WhitelistRule.objects.count()
            active_rules = WhitelistRule.objects.filter(active=True).count()
            inactive_rules = WhitelistRule.objects.filter(active=False).count()

            rules_by_baseline = WhitelistRule.objects.values(
                'baseline__name'
            ).annotate(count=Count('id'))
            rules_by_baseline_dict = {
                item['baseline__name']: item['count']
                for item in rules_by_baseline
            }

            # Recent Activity
            recent_sessions = MonitoringSession.objects.order_by(
                '-created_at'
            )[:5]
            recent_sessions_data = []
            for session in recent_sessions:
                recent_sessions_data.append({
                    'id': session.id,
                    'baseline_name': session.baseline.name,
                    'status': session.status,
                    'files_scanned': session.files_scanned,
                    'files_changed': session.files_changed,
                    'created_at': session.created_at.isoformat() if session.created_at else None
                })

            recent_alerts = Alert.objects.order_by('-created_at')[:5]
            recent_alerts_data = []
            for alert in recent_alerts:
                recent_alerts_data.append({
                    'id': alert.id,
                    'severity': alert.severity,
                    'title': alert.title,
                    'read': alert.read,
                    'created_at': alert.created_at.isoformat() if alert.created_at else None
                })

            # Health Status
            health_status = self._calculate_health_status(
                critical_alerts,
                failed_sessions,
                unacknowledged_changes
            )

            return {
                "timestamp": now.isoformat(),
                "health_status": health_status,
                "baselines": {
                    "total": total_baselines,
                    "monitored": baselines_monitored,
                    "coverage_percentage": (
                        (baselines_monitored / total_baselines * 100)
                        if total_baselines > 0 else 0
                    )
                },
                "monitoring_sessions": {
                    "total": total_sessions,
                    "completed": completed_sessions,
                    "failed": failed_sessions,
                    "running": running_sessions,
                    "last_24h": sessions_last_24h,
                    "last_7d": sessions_last_7d
                },
                "file_changes": {
                    "total": total_changes,
                    "unacknowledged": unacknowledged_changes,
                    "by_severity": changes_by_severity,
                    "last_24h": changes_last_24h,
                    "last_7d": changes_last_7d
                },
                "alerts": {
                    "total": total_alerts,
                    "unread": unread_alerts,
                    "archived": archived_alerts,
                    "active": active_alerts,
                    "critical": critical_alerts,
                    "by_severity": alerts_by_severity,
                    "last_24h": alerts_last_24h,
                    "last_7d": alerts_last_7d
                },
                "whitelist_rules": {
                    "total": total_rules,
                    "active": active_rules,
                    "inactive": inactive_rules,
                    "by_baseline": rules_by_baseline_dict
                },
                "recent_activity": {
                    "recent_sessions": recent_sessions_data,
                    "recent_alerts": recent_alerts_data
                }
            }

        except Exception as e:
            self.error = True
            self.set_status_code(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return {"message": f"Error retrieving dashboard summary: {str(e)}"}

    def _calculate_health_status(self, critical_alerts, failed_sessions, unacknowledged_changes):
        """Calculate overall health status based on key metrics"""
        if critical_alerts > 0 or failed_sessions > 0:
            return "critical"
        elif unacknowledged_changes > 5:
            return "warning"
        else:
            return "healthy"