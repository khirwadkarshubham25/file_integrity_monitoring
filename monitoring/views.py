import json

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from file_integrity_monitoring.services.view_services import ViewServices


# ============================================================================
# TEMPLATE VIEWS (Render HTML pages)
# ============================================================================

class Dashboard(View):
    """Render monitoring dashboard page"""

    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard.html')


class Baselines(View):
    """Render baselines management page"""

    def get(self, request, *args, **kwargs):
        return render(request, 'baselines.html')


class FileChanges(View):
    """Render file changes page"""

    def get(self, request, *args, **kwargs):
        return render(request, 'files_changes.html')


class Alerts(View):
    """Render alerts management page"""

    def get(self, request, *args, **kwargs):
        return render(request, 'alerts.html')


class MonitoringSessions(View):
    """Render monitoring sessions/history page"""

    def get(self, request, *args, **kwargs):
        return render(request, 'monitoring_sessions.html')


class WhitelistRules(View):
    """Render whitelist rules management page"""

    def get(self, request, *args, **kwargs):
        return render(request, 'whitelist_rules.html')

@method_decorator(csrf_exempt, name='dispatch')
class BaselinesView(View):
    def get(self, request, *args, **kwargs):
        page = request.GET.get('page', '1')
        page_size = request.GET.get('page_size', '10')
        sort_by = request.GET.get('sort_by', 'created_at')
        sort_order = request.GET.get('sort_order', 'desc')
        status = request.GET.get('status')
        user_id = request.GET.get('user_id')

        data = {
            'page': page,
            'page_size': page_size,
            'sort_by': sort_by,
            'sort_order': sort_order,
            'status': status,
            'user_id': user_id
        }

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='get_baselines')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        data['created_by'] = request.user.id if hasattr(request, 'user') else None

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='create_baseline')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)

    def put(self, request, *args, **kwargs):
        data = json.loads(request.body)
        data['updated_by'] = request.user.id if hasattr(request, 'user') else None

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='update_baseline')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)

    def delete(self, request, *args, **kwargs):
        data = json.loads(request.body)

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='delete_baseline')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
class BaselineDetailsView(View):
    def get(self, request, *args, **kwargs):
        baseline_id = request.GET.get('baseline_id')

        data = {'baseline_id': baseline_id}

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='get_baseline_details')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
class FileChangesView(View):
    def get(self, request, baseline_id=None, *args, **kwargs):
        page = request.GET.get('page', '1')
        page_size = request.GET.get('page_size', '10')
        sort_by = request.GET.get('sort_by', 'detected_at')
        sort_order = request.GET.get('sort_order', 'desc')
        severity = request.GET.get('severity')
        change_type = request.GET.get('change_type')
        acknowledged = request.GET.get('acknowledged')

        data = {
            'baseline_id': baseline_id,
            'page': page,
            'page_size': page_size,
            'sort_by': sort_by,
            'sort_order': sort_order,
            'severity': severity,
            'change_type': change_type,
            'acknowledged': acknowledged
        }

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='get_file_changes')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
class FileChangeDetailsView(View):
    def get(self, request, *args, **kwargs):
        change_id = request.GET.get('change_id')

        data = {'change_id': change_id}

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='get_file_change_details')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
class FileChangeAcknowledgeView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='acknowledge_file_change')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
class AlertsView(View):
    def get(self, request, *args, **kwargs):
        page = request.GET.get('page', '1')
        page_size = request.GET.get('page_size', '10')
        sort_by = request.GET.get('sort_by', 'created_at')
        sort_order = request.GET.get('sort_order', 'desc')
        severity = request.GET.get('severity')
        read = request.GET.get('read')
        is_archived = request.GET.get('is_archived')

        data = {
            'page': page,
            'page_size': page_size,
            'sort_by': sort_by,
            'sort_order': sort_order,
            'severity': severity,
            'read': read,
            'is_archived': is_archived
        }

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='get_alerts')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
class AlertDetailsView(View):
    def get(self, request, *args, **kwargs):
        alert_id = request.GET.get('alert_id')

        data = {'alert_id': alert_id}

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='get_alert_details')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
class AlertReadView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        data['read_by'] = request.user.id if hasattr(request, 'user') else None

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='mark_alert_read')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
class AlertArchiveView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='archive_alert')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
class MonitoringSessionsView(View):
    def get(self, request, *args, **kwargs):
        page = request.GET.get('page', '1')
        page_size = request.GET.get('page_size', '10')
        sort_by = request.GET.get('sort_by', 'start_time')
        sort_order = request.GET.get('sort_order', 'desc')
        baseline_id = request.GET.get('baseline_id')
        status = request.GET.get('status')

        data = {
            'page': page,
            'page_size': page_size,
            'sort_by': sort_by,
            'sort_order': sort_order,
            'baseline_id': baseline_id,
            'status': status
        }

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='get_monitoring_sessions')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
class MonitoringSessionDetailsView(View):
    def get(self, request, *args, **kwargs):
        session_id = request.GET.get('monitor_session_id')

        data = {'monitor_session_id': session_id}

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='get_monitoring_session_details')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
class MonitoringSessionStartView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        kwargs.update({'data': data})

        service_obj = ViewServices(service_name='start_monitoring_session')
        status_code, response = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(response, status=status_code)

@method_decorator(csrf_exempt, name='dispatch')
class WhitelistRulesView(View):
    def get(self, request, *args, **kwargs):
        page = request.GET.get('page', '1')
        page_size = request.GET.get('page_size', '10')
        baseline_id = request.GET.get('baseline_id')
        active = request.GET.get('active')

        data = {
            'page': page,
            'page_size': page_size,
            'baseline_id': baseline_id,
            'active': active
        }

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='get_whitelist_rules')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        data['user_id'] = request.user.id if hasattr(request, 'user') else None

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='create_whitelist_rule')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)

    def put(self, request, *args, **kwargs):
        data = json.loads(request.body)

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='update_whitelist_rule')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)

    def delete(self, request, *args, **kwargs):
        data = json.loads(request.body)

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='delete_whitelist_rule')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
class WhitelistRuleDetailsView(View):
    def get(self, request, *args, **kwargs):
        rule_id = request.GET.get('rule_id')

        data = {'rule_id': rule_id}

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='get_whitelist_rule_details')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
class DashboardSummaryView(View):

    def get(self, request, *args, **kwargs):
        data = {}

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='get_dashboard_summary')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)