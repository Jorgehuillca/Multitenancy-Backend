"""
Constantes del sistema
"""

# Roles del sistema
ROLES = {
    'ADMIN': 'Admin',
    'USER': 'User',
    'MEMBER': 'Member'
}

# Estados de usuario
USER_STATUS = {
    'ACTIVE': True,
    'INACTIVE': False
}

# Tipos de permisos
PERMISSION_TYPES = {
    'CREATE': 'add',
    'READ': 'view',
    'UPDATE': 'change',
    'DELETE': 'delete'
}

# Configuración de JWT (informativo)
# Nota: la configuración EFECTIVA de SimpleJWT se hace en settings.SIMPLE_JWT.
# Estos valores NO son usados por la autenticación JWT del proyecto; se
# mantienen solo como referencia para otras utilidades.
JWT_SETTINGS = {
    'ACCESS_TOKEN_LIFETIME_MIN': None,  # ver settings.SIMPLE_JWT
    'REFRESH_TOKEN_LIFETIME_MIN': None,  # ver settings.SIMPLE_JWT
}

# Mensajes del sistema
MESSAGES = {
    'USER_CREATED': 'Usuario creado exitosamente',
    'USER_UPDATED': 'Usuario actualizado exitosamente',
    'USER_DELETED': 'Usuario eliminado exitosamente',
    'PASSWORD_CHANGED': 'Contraseña cambiada exitosamente',
    'LOGIN_SUCCESS': 'Inicio de sesión exitoso',
    'LOGOUT_SUCCESS': 'Cierre de sesión exitoso',
    'PERMISSION_DENIED': 'No tienes permisos para realizar esta acción',
    'INVALID_CREDENTIALS': 'Credenciales inválidas',
    'USER_NOT_FOUND': 'Usuario no encontrado'
} 


class SystemConstants:
    """
    Contenedor para compatibilidad: permite importar SystemConstants y acceder a
    constantes como atributos de clase.
    """
    ROLES = ROLES
    USER_STATUS = USER_STATUS
    PERMISSION_TYPES = PERMISSION_TYPES
    JWT_SETTINGS = JWT_SETTINGS
    MESSAGES = MESSAGES