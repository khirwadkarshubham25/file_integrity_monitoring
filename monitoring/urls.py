from django.urls import path

from monitoring import views

urlpatterns = [
    # Template routes (render HTML pages)
    path('dashboard', views.Dashboard.as_view(), name='dashboard'),
    path('baselines', views.Baselines.as_view(), name='baselines'),
    path('fileChanges', views.FileChanges.as_view(), name='fileChanges'),
    path('alerts', views.Alerts.as_view(), name='alerts'),
    path('monitoringSessions', views.MonitoringSessions.as_view(), name='monitoringSessions'),
    path('whitelistRules', views.WhitelistRules.as_view(), name='whitelistRules'),

    # API routes (JSON responses)
    path('api/baselines', views.BaselinesView.as_view(), name='api_baselines'),
    path('api/baseline-details', views.BaselineDetailsView.as_view(), name='api_baseline_details'),
    path('api/file-changes', views.FileChangesView.as_view(), name='api_file_changes'),
    path('api/file-change-details', views.FileChangeDetailsView.as_view(), name='api_file_change_details'),
    path('api/file-change-acknowledge', views.FileChangeAcknowledgeView.as_view(), name='api_file_change_acknowledge'),
    path('api/alerts', views.AlertsView.as_view(), name='api_alerts'),
    path('api/alert-details', views.AlertDetailsView.as_view(), name='api_alert_details'),
    path('api/alert-read', views.AlertReadView.as_view(), name='api_alert_read'),
    path('api/alert-archive', views.AlertArchiveView.as_view(), name='api_alert_archive'),
    path('api/monitoring-sessions', views.MonitoringSessionsView.as_view(), name='api_monitoring_sessions'),
    path('api/monitoring-session-details', views.MonitoringSessionDetailsView.as_view(),
         name='api_monitoring_session_details'),
    path('api/monitoring-session-start', views.MonitoringSessionStartView.as_view(), name='api_monitoring_session_start'),
    path('api/whitelist-rules', views.WhitelistRulesView.as_view(), name='api_whitelist_rules'),
    path('api/whitelist-rule-details', views.WhitelistRuleDetailsView.as_view(), name='api_whitelist_rule_details'),
    path('api/dashboard-summary', views.DashboardSummaryView.as_view(), name='api_dashboard_summary'),
]