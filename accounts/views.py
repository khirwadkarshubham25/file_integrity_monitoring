import json

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView

from file_integrity_monitoring.services.view_services import ViewServices

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        kwargs.update({
            'data': data
        })
        service_obj = ViewServices(service_name='login_user')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        kwargs.update({
            'data': data
        })
        service_obj = ViewServices(service_name='register_user')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
class UsersView(ListView):
    def get(self, request, *args, **kwargs):
        page = request.GET.get('page', '1')
        page_size = request.GET.get('page_size', '10')
        sort_by = request.GET.get('sort_by', 'created_at')
        sort_order = request.GET.get('sort_order', 'desc')

        data = {
            'page': page,
            'page_size': page_size,
            'sort_by': sort_by,
            'sort_order': sort_order
        }

        kwargs.update({
            'data': data
        })
        service_obj = ViewServices(service_name='get_users')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
class UserDetailsView(View):
    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id', 0)

        data = {
            'user_id': user_id
        }

        kwargs.update({
            'data': data
        })
        service_obj = ViewServices(service_name='get_user_details')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        kwargs.update({
            'data': data
        })
        service_obj = ViewServices(service_name='create_users')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)

    def put(self, request, *args, **kwargs):
        data = json.loads(request.body)

        kwargs.update({
            'data': data
        })
        service_obj = ViewServices(service_name='update_users')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)

    def delete(self, request, *args, **kwargs):
        data = json.loads(request.body)

        kwargs.update({
            'data': data
        })
        service_obj = ViewServices(service_name='delete_users')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
class AuditLogsView(ListView):
    def get(self, request, *args, **kwargs):
        page = request.GET.get('page', '1')
        page_size = request.GET.get('page_size', '10')
        sort_by = request.GET.get('sort_by', 'created_at')
        sort_order = request.GET.get('sort_order', 'desc')
        action = request.GET.get('action')
        resource_type = request.GET.get('resource_type')

        data = {
            'page': page,
            'page_size': page_size,
            'sort_by': sort_by,
            'sort_order': sort_order,
            'action': action,
            'resource_type': resource_type
        }

        kwargs.update({
            'data': data
        })
        service_obj = ViewServices(service_name='get_audit_logs')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
class AuditLogDetailsView(View):
    def get(self, request, *args, **kwargs):
        log_id = request.GET.get('log_id')
        data = {
            'log_id': log_id
        }

        kwargs.update({
            'data': data
        })
        service_obj = ViewServices(service_name='get_audit_log_details')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)


@method_decorator(csrf_exempt, name='dispatch')
class RolesView(View):
    def get(self, request, *args, **kwargs):
        data = {
            'page': request.GET.get('page', '1'),
            'page_size': request.GET.get('page_size', '10')
        }

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='get_roles')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='create_role')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)

    def put(self, request, *args, **kwargs):
        data = json.loads(request.body)

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='update_role')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)

    def delete(self, request, *args, **kwargs):
        data = json.loads(request.body)

        kwargs.update({'data': data})
        service_obj = ViewServices(service_name='delete_role')
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)


class Login(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'login.html')

class Register(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'register.html')

class Users(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'users.html')

class AuditLogs(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'audit_logs.html')

class Roles(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'roles.html')