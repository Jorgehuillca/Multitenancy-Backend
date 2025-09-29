from .auth import LoginView, RegisterView
from .user import UserListView, UserCreateView, UserEditView, AdminUserDeleteView
from .permission import PermissionView
from .role import RoleListView, RoleCreateView, RoleEditView, RoleDeleteView

__all__ = [
    'LoginView', 'RegisterView',
    'UserListView', 'UserCreateView', 'UserEditView', 'AdminUserDeleteView',
    'PermissionView', 'RoleListView', 'RoleCreateView', 'RoleEditView', 'RoleDeleteView'
]