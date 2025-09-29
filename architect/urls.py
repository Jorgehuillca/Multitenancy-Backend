from django.urls import path
from .views.auth import LoginView, RegisterView, LogoutView
from .views.user import UserListView, UserCreateView, UserEditView, AdminUserDeleteView
from .views.permission import PermissionView
from .views.role import RoleListView, RoleCreateView, RoleEditView, RoleDeleteView

app_name = 'architect'

urlpatterns = [
    # Autenticación
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    
    # Usuarios
    path('users/', UserListView.as_view(), name='users'),  # GET
    path('users/create/', UserCreateView.as_view(), name='users-create'),  # POST
    path('users/<int:pk>/edit/', UserEditView.as_view(), name='users-edit'),  # PUT/PATCH
    path('users/<int:pk>/delete/', AdminUserDeleteView.as_view(), name='users-delete'),  # DELETE (hard delete)
    
    # Permisos
    path('permissions/', PermissionView.as_view(), name='permissions'),
    
    # Roles (CRUD admin-only)
    path('roles/', RoleListView.as_view(), name='roles'),                 # GET
    path('roles/create/', RoleCreateView.as_view(), name='roles-create'), # POST
    path('roles/<int:pk>/edit/', RoleEditView.as_view(), name='roles-edit'),  # PUT/PATCH
    path('roles/<int:pk>/delete/', RoleDeleteView.as_view(), name='roles-delete'),  # DELETE
] 