from django.urls import path

from accounts import views

urlpatterns = [
    path('api/login', views.LoginView.as_view(), name='api-login'),
    path('api/register', views.RegisterView.as_view(), name='api-register'),
    path('api/users', views.UsersView.as_view(), name='api-users'),
    path('api/users-details', views.UserDetailsView.as_view(), name='api-user_details'),
    path('api/audit-logs', views.AuditLogsView.as_view(), name='api-audit_logs'),
    path('api/audit-log-details', views.AuditLogDetailsView.as_view(), name='api-audit_log-details'),
    path('api/roles', views.RolesView.as_view(), name='api-roles'),

    path('login', views.Login.as_view(), name='login'),
    path('register', views.Register.as_view(), name='register'),
    path('users', views.Users.as_view(), name='users'),
    path('audit-logs', views.AuditLogs.as_view(), name='audit_logs'),
    path('roles', views.Roles.as_view(), name='roles'),
]