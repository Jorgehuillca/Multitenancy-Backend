from django.urls import path
from .views.auth import LoginView, RegisterView
from .views.user import UserView
from .views.permission import PermissionView, RoleView, RoleDetailView

app_name = 'architect'

urlpatterns = [
    # Autenticación
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    
    # Usuarios
    path('users/', UserView.as_view(), name='users'),
    
    # Permisos
    path('permissions/', PermissionView.as_view(), name='permissions'),
    
    # Roles
    path('roles/', RoleView.as_view(), name='roles'),                             # GET (list)
    path('roles/create/', RoleView.as_view(), name='roles_create'),               # POST (create)
    path('roles/<int:id>/', RoleDetailView.as_view(), name='role_detail'),        # GET (detail)
    path('roles/<int:id>/edit/', RoleDetailView.as_view(), name='role_edit'),     # PUT/PATCH (update)
    path('roles/<int:id>/delete/', RoleDetailView.as_view(), name='role_delete'), # DELETE (delete)
] 