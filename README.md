# 🏛️ API Endpoints Completo - Backend Reflexo Multitenancy

## 🌐 Base URL
xd
```
http://localhost:8000/   # Desarrollo local
```

## 📜 Estándar de URLs Unificado

Todas las APIs siguen el patrón: `/api/[modulo]/[recurso]`

---

## 🧩 Módulo 1: Arquitectura y Autenticación (/api/architect/)

### 🔐 Autenticación

| Método | Endpoint                         | Descripción           | Autenticación |
|-------:|----------------------------------|-----------------------|---------------|
|   POST | `/api/architect/auth/register/`  | Registro de usuario   | No requerida  |
|   POST | `/api/architect/auth/login/`     | Login de usuario      | No requerida  |
|   POST | `/api/architect/auth/logout/`    | Logout de usuario     | Requerida     |

#### 🧪 Ejemplos de Autenticación

##### 🆕 Registro de Usuario

- Método: POST
- URL: `http://localhost:8000/api/architect/auth/register/`
- Headers:
  - `Content-Type: application/json`
- Body → raw → JSON

```json
{
  "email": "nuevo@acme.com",
  "user_name": "nuevo_usuario",
  "document_number": "12345678",
  "name": "Nombre",
  "paternal_lastname": "ApellidoPaterno",
  "maternal_lastname": "ApellidoMaterno",
  "password": "TuPasswordSegura",
  "password_confirm": "TuPasswordSegura"
}
```

- Respuesta 201 (ejemplo):

```json
{ "message": "Usuario registrado con éxito" }
```

> Validaciones de contraseña: mínimo 8 caracteres y no debe ser común (p. ej. "password", "123456").

##### 🔓 Login de Usuario

- Método: POST
- URL: `http://localhost:8000/api/architect/auth/login/`
- Headers:
  - `Content-Type: application/json`
- Body → raw → JSON

```json
{
  "email": "nuevo@acme.com",
  "password": "TuPasswordSegura"
}
```

- Respuesta 200 (ejemplo):

```json
{
  "email": "nuevo@acme.com",
  "refresh": "toquen de refresco",
  "access": "toquen de acceso",
  "user_id": 20
}
```

##### 🚪 Logout de Usuario

- Método: POST
- URL: `http://localhost:8000/api/architect/auth/logout/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

```json
{}
```

- Respuesta 200 (ejemplo):

```json
{
  "detail": "Sesión cerrada. Token revocado."
}
```

## 👥 Usuarios (/api/architect/users/)

### 🔗 Endpoints

| Método | Endpoint                                | Descripción                   | Autenticación |
|-------:|-----------------------------------------|-------------------------------|---------------|
|    GET | `/api/architect/users/`                 | Listar usuarios               | Requerida     |
|   POST | `/api/architect/users/create/`          | Crear usuario                 | Requerida     |
|    PUT | `/api/architect/users/<int:pk>/edit/`   | Editar usuario (completo)     | Requerida     |
|  PATCH | `/api/architect/users/<int:pk>/edit/`   | Editar usuario (parcial)      | Requerida     |
| DELETE | `/api/architect/users/<int:pk>/delete/` | Eliminar usuario (hard delete) | Requerida     |

> ℹ️ Notas:
> - DELETE realiza un borrado definitivo (hard delete). No queda rastro en la base de datos ni en Django Admin.
> - Un admin que no sea superusuario no puede eliminar a un superusuario.
> - El endpoint de creación acepta `is_staff` e `is_superuser` solamente cuando el solicitante es superusuario; de lo contrario se ignoran y quedan en `false`.

### 🧪 Ejemplos

#### 📋 Listar Usuarios

- Método: GET
- URL: `http://localhost:8000/api/architect/users/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

**Control de Acceso:**
- **Superusuarios**: Pueden ver todos los usuarios registrados en el sistema
- **Usuarios staff**: Solo pueden ver su propio perfil (devuelto como array con un elemento)
- **Usuarios normales**: Acceso denegado (403 Forbidden)

**Respuesta 200 para superusuarios** (ejemplo):

```json
[
  {
    "id": 1,
    "email": "admin@acme.com",
    "user_name": "admin",
    "name": "Admin",
    "paternal_lastname": "User",
    "maternal_lastname": "Root",
    "is_active": true,
    "is_staff": false,
    "is_superuser": true
  },
  {
    "id": 2,
    "email": "staff@acme.com",
    "user_name": "staff",
    "name": "Staff",
    "paternal_lastname": "User",
    "maternal_lastname": "Member",
    "is_active": true,
    "is_staff": true,
    "is_superuser": false
  }
]
```

**Respuesta 200 para usuarios staff** (ejemplo):

```json
[
  {
    "id": 2,
    "email": "staff@acme.com",
    "user_name": "staff",
    "name": "Staff",
    "paternal_lastname": "User",
    "maternal_lastname": "Member",
    "is_active": true,
    "is_staff": true,
    "is_superuser": false
  }
]
```

**Respuesta 403 para usuarios normales**:

```json
{
  "error": "No tienes permisos para acceder a esta información"
}
```

#### ➕ Crear Usuario

- Método: POST
- URL: `http://localhost:8000/api/architect/users/create/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

```json
{
  "email": "u@example.com",
  "user_name": "userexample",
  "name": "User",
  "document_number": "87654321",
  "paternal_lastname": "Example",
  "maternal_lastname": "Demo",
  "sex": "M",
  "phone": "999888777",
  "password": "Passw0rd#123",
  "is_active": true,
  "is_staff": true,
  "is_superuser": false
}
```

> 🔒 Seguridad: Solo un superusuario puede establecer `is_staff` o `is_superuser` al crear usuarios. Si el solicitante no es superusuario, estos campos serán ignorados y guardados como `false`.

Respuesta 201 (ejemplo):

```json
{
  "id": 23,
  "user_name": "userexample",
  "email": "u@example.com",
  "name": "User",
  "document_number": "87654321",
  "paternal_lastname": "Example",
  "maternal_lastname": "Demo",
  "phone": "999888777",
  "sex": "M",
  "account_statement": "A",
  "is_active": true,
  "is_staff": true,
  "is_superuser": false,
  "created_at": "2025-09-25T19:52:30.870263Z",
  "updated_at": "2025-09-25T19:52:30.870273Z"
}
```

> Nota: El campo `password` es write-only y no aparece en la respuesta. Los campos `name`, `document_number`, `paternal_lastname`, `maternal_lastname`, `sex`, `is_staff` e `is_superuser` ahora aparecen en la respuesta. El campo `phone` puede venir `null` si no se envía. `account_statement` es un código/valor controlado por el sistema.

#### ✏️ Editar Usuario (PUT completo)

- Método: PUT
- URL: `http://localhost:8000/api/architect/users/21/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición se aplica al usuario identificado por el `id` en la URL (en el ejemplo, `21`).

```json
{
  "name": "Usuario",
  "paternal_lastname": "Actualizado",
  "maternal_lastname": "Total",
  "user_name": "userexample",
  "document_number": "87654321",
  "email": "u@example.com"
}
```

Respuesta 200 (ejemplo): cuerpo con el usuario actualizado.

#### 🩹 Editar Usuario (PATCH parcial)

- Método: PATCH
- URL: `http://localhost:8000/api/architect/users/21/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición parcial se aplica al usuario identificado por el `id` en la URL.

```json
{
  "user_name": "SoloNombre"
}
```

#### 🗑️ Eliminar Usuario (hard delete)

- Método: DELETE
- URL: `http://localhost:8000/api/architect/users/21/delete/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

> ℹ️ Nota: La eliminación se aplica al usuario identificado por el `id` en la URL.

Respuesta 200 (ejemplo):

```json
{ "message": "Usuario eliminado definitivamente" }
```

---

## 🎭 Roles (/api/architect/roles/)

### 🔗 Endpoints

| Método | Endpoint                                | Descripción                   | Autenticación | Permisos     |
|-------:|-----------------------------------------|-------------------------------|---------------|--------------|
|    GET | `/api/architect/roles/`                | Listar roles                  | Requerida     | Admin only   |
|   POST | `/api/architect/roles/create/`          | Crear rol                     | Requerida     | Admin only   |
|    PUT | `/api/architect/roles/<int:pk>/edit/`   | Editar rol (completo)         | Requerida     | Admin only   |
|  PATCH | `/api/architect/roles/<int:pk>/edit/`   | Editar rol (parcial)          | Requerida     | Admin only   |
| DELETE | `/api/architect/roles/<int:pk>/delete/`| Eliminar rol                  | Requerida     | Admin only   |

> ℹ️ Notas:
> - Todos los endpoints requieren autenticación con Bearer Token
> - Solo usuarios administradores pueden usar estos endpoints (`rol = 'Admin'` o `is_superuser = True`)
> - Los roles se ordenan alfabéticamente por nombre en las respuestas

### 🧪 Ejemplos de Roles

#### 📋 Listar Roles

- Método: GET
- URL: `http://localhost:8000/api/architect/roles/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
[
    {
        "id": 1,
        "name": "Admin",
        "guard_name": "api",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    },
    {
        "id": 2,
        "name": "Member",
        "guard_name": "api",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    }
]
```

- Respuesta 403 Forbidden (No admin):

```json
{
    "detail": "You do not have permission to perform this action."
}
```

#### ➕ Crear Rol

- Método: POST
- URL: `http://localhost:8000/api/architect/roles/create/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

```json
{
    "name": "Manager",
    "guard_name": "api"
}
```

- Respuesta 201 Created (ejemplo):

```json
{
    "id": 3,
    "name": "Manager",
    "guard_name": "api",
    "created_at": "2024-01-15T12:00:00Z",
    "updated_at": "2024-01-15T12:00:00Z"
}
```

- Respuesta 400 Bad Request (datos inválidos):

```json
{
    "name": [
        "This field is required."
    ]
}
```

#### ✏️ Editar Rol (PUT completo)

- Método: PUT
- URL: `http://localhost:8000/api/architect/roles/3/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición se aplica al rol identificado por el `id` en la URL.

```json
{
    "name": "Senior Manager",
    "guard_name": "api"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "id": 3,
    "name": "Senior Manager",
    "guard_name": "api",
    "created_at": "2024-01-15T12:00:00Z",
    "updated_at": "2024-01-15T12:05:00Z"
}
```

#### 🩹 Editar Rol (PATCH parcial)

- Método: PATCH
- URL: `http://localhost:8000/api/architect/roles/3/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición parcial se aplica al rol identificado por el `id` en la URL.

```json
{
    "name": "Lead Manager"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "id": 3,
    "name": "Lead Manager",
    "guard_name": "api",
    "created_at": "2024-01-15T12:00:00Z",
    "updated_at": "2024-01-15T12:10:00Z"
}
```

#### 🗑️ Eliminar Rol

- Método: DELETE
- URL: `http://localhost:8000/api/architect/roles/3/delete/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

> ℹ️ Nota: La eliminación se aplica al rol identificado por el `id` en la URL.

- Respuesta 200 (ejemplo):

```json
{
    "message": "Rol eliminado"
}
```

- Respuesta 404 Not Found:

```json
{
    "error": "Rol no encontrado"
}
```

### 📝 Campos del Modelo Role

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | Integer | Auto | ID único del rol |
| `name` | String(255) | Sí | Nombre del rol |
| `guard_name` | String(255) | No | Tipo de guard para el rol |
| `created_at` | DateTime | Auto | Fecha de creación |
| `updated_at` | DateTime | Auto | Fecha de última actualización |

### 🚨 Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| `400` | Datos inválidos | Revisar formato JSON y campos requeridos |
| `401` | No autenticado | Verificar token JWT válido |
| `403` | No autorizado | Usuario debe ser admin (`rol = 'Admin'`) |
| `404` | Rol no encontrado | Verificar que el ID del rol existe |
| `500` | Error del servidor | Revisar logs del servidor |

---

## 🧩 Módulo 2: Perfiles de Usuario (/api/profiles/)

### 👤 Gestión de Usuario

| Método | Endpoint                                  | Descripción                               | Autenticación |
|-------:|-------------------------------------------|-------------------------------------------|---------------|
|    GET | `/api/profiles/users/me/`                 | Mi perfil de usuario                      | Requerida     |
|    PUT | `/api/profiles/users/me/update/`          | Actualizar mi perfil (completo)           | Requerida     |
|  PATCH | `/api/profiles/users/me/update/`          | Actualizar campos puntuales de mi perfil  | Requerida     |
|   POST | `/api/profiles/users/me/create/photo/`    | Subir foto de perfil                      | Requerida     |
| DELETE | `/api/profiles/users/me/delete/photo/`    | Eliminar foto de perfil (hard delete)     | Requerida     |
| DELETE | `/api/profiles/users/me/delete/`          | Eliminar mi usuario (hard delete)         | Requerida     |
|    GET | `/api/profiles/users/search/`             | Buscar usuarios                           | Requerida     |
|    GET | `/api/profiles/users/profile/`            | Ver mi perfil completo                    | Requerida     |

> ℹ️ Notas:
> - Todas las rutas operan sobre el usuario autenticado mediante `me/` (no requieren id).
> - Ambos DELETE (foto y usuario) son hard delete por defecto: no dejan rastro en la base de datos ni en el almacenamiento.

#### 🧪 Ejemplos de Perfiles

##### 👤 Obtener Mi Perfil

- Método: GET
- URL: `http://localhost:8000/api/profiles/users/me/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
  "id": 23,
  "user_name": "userexample",
  "email": "u@example.com",
  "name": "User",
  "paternal_lastname": "Example",
  "maternal_lastname": "Demo",
  "full_name": "User Example Demo",
  "phone": "999888777",
  "account_statement": "A",
  "is_active": true,
  "date_joined": "2025-09-25T19:52:30.323039Z",
  "last_login": null,
  "profile_photo_url": null,
  "document_number": "87654321",
  "document_type": null,
  "sex": "M",
  "country": null,
  "photo_url": null
}
```

##### ✏️ Actualizar Mi Perfil (PUT)

- Método: PUT
- URL: `http://localhost:8000/api/profiles/users/me/update/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

```json
{
  "user_name": "eduardo",
  "name": "Eduardo",
  "paternal_lastname": "Pérez",
  "maternal_lastname": "Gómez",
  "phone": "+51 988 777 666"
}
```

##### 🩹 Actualizar Campos Puntuales (PATCH)

- Método: PATCH
- URL: `http://localhost:8000/api/profiles/users/me/update/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

```json
{
  "phone": "+51 955 444 333"
}
```

##### 📸 Subir Foto de Perfil

- Método: POST
- URL: `http://localhost:8000/api/profiles/users/me/create/photo/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`
  - `Content-Type: multipart/form-data`
- Body → form-data
  - **Key:** `photo_file`
  - **Type:** Seleccionar `File` (no Text)
  - **Value:** Seleccionar el archivo de imagen desde tu computadora

- Respuesta 201 (ejemplo):

```json
{
    "message": "Foto de perfil actualizada exitosamente",
    "photo_url": "/media/users/photos/mesa_redonda.JPG"
}
```

> **Nota:** Según la foto seleccionada, te devolverá un mensaje de confirmación y la URL de la foto subida. El nombre del archivo en `photo_url` corresponderá al archivo que hayas seleccionado.

##### 🗑️ Eliminar Foto de Perfil (hard delete)

- Método: DELETE
- URL: `http://localhost:8000/api/profiles/users/me/delete/photo/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{ "message": "Foto de perfil eliminada definitivamente" }
```

##### 🗑️ Eliminar Mi Usuario (hard delete)

- Método: DELETE
- URL: `http://localhost:8000/api/profiles/users/me/delete/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{ "message": "Usuario eliminado definitivamente" }
```

##### 🔍 Buscar Usuarios

- Método: GET
- URL: `http://localhost:8000/api/profiles/users/search/?q=eduard`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "user_name": "eduard",
            "email": "admin@gmail.com",
            "name": "Fabrizio",
            "paternal_lastname": "Alvarez",
            "maternal_lastname": "Ponce",
            "full_name": "Fabrizio Alvarez Ponce",
            "phone": "987654321",
            "account_statement": "A",
            "is_active": true,
            "date_joined": "2025-09-04T15:51:50.654297Z",
            "last_login": "2025-09-25T17:57:49.356460Z",
            "profile_photo_url": "/media/users/photos/1682ed456f900f7f038f0e007ea91c13_qxLBTE8.jpg",
            "document_number": "87654326",
            "document_type": null,
            "sex": "M",
            "country": null,
            "photo_url": "http://localhost:8000/media/users/photos/1682ed456f900f7f038f0e007ea91c13_qxLBTE8.jpg"
        }
    ]
}
```

> **Nota:** La búsqueda funciona por coincidencias parciales en el nombre de usuario. Si buscas "eduard", encontrará usuarios con nombres como "eduard", "eduardo", "eduardito", etc. También puede devolver múltiples resultados si hay varios usuarios con nombres similares.

##### 📋 Ver Mi Perfil Completo

- Método: GET
- URL: `http://localhost:8000/api/profiles/users/profile/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "id": 23,
    "user_name": "eduardo",
    "email": "u@example.com",
    "name": "Eduardo",
    "paternal_lastname": "Pérez",
    "maternal_lastname": "Gómez",
    "full_name": "Eduardo Pérez Gómez",
    "phone": "+51 955 444 333",
    "account_statement": "A",
    "is_active": true,
    "date_joined": "2025-09-25T19:52:30.323039Z",
    "last_login": null,
    "profile_photo_url": null,
    "document_number": "87654321",
    "document_type": null,
    "sex": "M",
    "country": null,
    "photo_url": null
}
```

> **Nota:** Este endpoint muestra toda la información completa de tu perfil del usuario con el que hayas iniciado sesión vía token. Incluye todos los datos personales, información de cuenta y configuraciones del perfil.


## 🔒 Gestión de Contraseñas (/api/profiles/password/)

### 🔐 Endpoints

| Método | Endpoint                                    | Descripción                               | Autenticación |
|-------:|---------------------------------------------|-------------------------------------------|---------------|
|   POST | `/api/profiles/password/change/`            | Cambiar contraseña                        | Requerida     |
|   POST | `/api/profiles/password/reset/`             | Solicitar reset de contraseña             | No requerida  |
|   POST | `/api/profiles/password/reset/confirm/`     | Confirmar reset de contraseña             | No requerida  |
|   POST | `/api/profiles/password/strength/`          | Validar fortaleza de contraseña          | No requerida  |
|    GET | `/api/profiles/password/history/`           | Ver historial de contraseñas              | Requerida     |
|    GET | `/api/profiles/password/policy/`            | Ver política de contraseñas              | No requerida  |

### 🧪 Ejemplos de Contraseñas

#### 🔄 Cambiar Contraseña

- Método: POST
- URL: `http://localhost:8000/api/profiles/password/change/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

```json
{
    "current_password": "mi_contraseña_actual",
    "new_password": "NuevaContraseña#123",
    "new_password_confirm": "NuevaContraseña#123"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "message": "Contraseña cambiada exitosamente"
}
```

- Respuesta 400 Bad Request (datos inválidos):

```json
{
    "current_password": ["La contraseña actual es incorrecta"]
}
```

#### 🔓 Solicitar Reset de Contraseña

- Método: POST
- URL: `http://localhost:8000/api/profiles/password/reset/`
- Headers:
  - `Content-Type: application/json`
- Body → raw → JSON

```json
{
    "email": "usuario@example.com"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "message": "Código de verificación enviado exitosamente",
    "code": "123456",
    "expires_at": "2025-09-26T04:30:00Z"
}
```

#### ✅ Confirmar Reset de Contraseña

- Método: POST
- URL: `http://localhost:8000/api/profiles/password/reset/confirm/`
- Headers:
  - `Content-Type: application/json`
- Body → raw → JSON

```json
{
    "code": "123456",
    "new_password": "NuevaContraseña#123",
    "new_password_confirm": "NuevaContraseña#123"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "message": "Contraseña restablecida exitosamente"
}
```

#### 💪 Validar Fortaleza de Contraseña

- Método: POST
- URL: `http://localhost:8000/api/profiles/password/strength/`
- Headers:
  - `Content-Type: application/json`
- Body → raw → JSON

```json
{
    "password": "MiNuevaContraseña#123"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "is_strong": true,
    "score": 8,
    "suggestions": []
}
```

#### 📜 Ver Historial de Contraseñas

- Método: GET
- URL: `http://localhost:8000/api/profiles/password/history/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "password_history": [
        {
            "date": "2025-09-25T10:30:00Z",
            "last_updated": "2025-09-25T10:30:00Z"
        }
    ]
}
```

#### 📋 Ver Política de Contraseñas

- Método: GET
- URL: `http://localhost:8000/api/profiles/password/policy/`
- Headers:
  - `Content-Type: application/json`

- Respuesta 200 (ejemplo):

```json
{
    "rules": {
        "min_length": 8,
        "max_length": 128,
        "require_letters": true,
        "require_numbers": true,
        "require_symbols": true,
        "common_passwords_check": true
    },
    "message": "Su contraseña debe tener al menos 8 caracteres, contener letras, números y símbolos"
}
```

---

## ✉️ Verificación de Email (/api/profiles/verification/)

### 🔐 Endpoints

| Método | Endpoint                                            | Descripción                               | Autenticación |
|-------:|-----------------------------------------------------|-------------------------------------------|---------------|
|   POST | `/api/profiles/verification/code/`                  | Solicitar código de verificación         | Requerida     |
|   POST | `/api/profiles/verification/code/resend/`           | Reenviar código verificación             | Requerida     |
|   POST | `/api/profiles/verification/email/change/`          | Solicitar cambio de email                 | Requerida     |
|   POST | `/api/profiles/verification/email/change/confirm/` | Confirmar cambio de email                  | Requerida     |
|   POST | `/api/profiles/verification/email/confirm/`        | Confirmar verificación de email           | Requerida     |
|   POST | `/api/profiles/verification/email/`                | Solicitar verificación de email          | No requerida  |
|    GET | `/api/profiles/verification/status/`               | Ver estado de verificación                | Requerida     |

### 🧪 Ejemplos de Verificación

#### 📬 Solicitar Código de Verificación

- Método: POST
- URL: `http://localhost:8000/api/profiles/verification/code/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

```json
{
    "verification_type": "email_change",
    "target_email": "nuevo@example.com"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "message": "Código de verificación enviado exitosamente",
    "code": "123456",
    "expires_at": "2025-09-26T04:30:00Z",
    "verification_type": "email_change"
}
```

#### 🔄 Reenviar Código de Verificación

- Método: POST
- URL: `http://localhost:8000/api/profiles/verification/code/resend/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

```json
{
    "verification_type": "email_change",
    "target_email": "nuevo@example.com"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "message": "Código de verificación reenviado exitosamente",
    "code": "789012",
    "expires_at": "2025-09-26T04:35:00Z"
}
```

#### 📧 Solicitar Cambio de Email

- Método: POST
- URL: `http://localhost:8000/api/profiles/verification/email/change/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

```json
{
    "new_email": "nuevo@example.com"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "message": "Código de verificación enviado al nuevo email",
    "code": "345678",
    "expires_at": "2025-09-26T04:30:00Z"
}
```

#### ✅ Confirmar Cambio de Email

- Método: POST
- URL: `http://localhost:8000/api/profiles/verification/email/change/confirm/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

```json
{
    "code": "345678"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "message": "Email cambiado exitosamente"
}
```

#### 📧 Solicitar Verificación de Email (Registro)

- Método: POST
- URL: `http://localhost:8000/api/profiles/verification/email/`
- Headers:
  - `Content-Type: application/json`
- Body → raw → JSON

```json
{
    "email": "usuario@example.com"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "message": "Código de verificación enviado exitosamente",
    "code": "456789",
    "expires_at": "2025-09-26T04:30:00Z"
}
```

#### ✅ Confirmar Verificación de Email

- Método: POST
- URL: `http://localhost:8000/api/profiles/verification/email/confirm/`
- Headers:
  - `Content-Type: application/json`
- Body → raw → JSON

```json
{
    "code": "456789"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "message": "Email verificado exitosamente"
}
```

#### 📊 Ver Estado de Verificación

- Método: GET
- URL: `http://localhost:8000/api/profiles/verification/status/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "user_email": "usuario@example.com",
    "email_verified": true,
    "active_verifications": [
        {
            "verification_type": "email_change",
            "expires_at": "2025-09-26T04:30:00Z",
            "attempts_remaining": 5,
            "is_valid": true
        }
    ]
}
```

### 🚨 Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| `400` | Datos inválidos | Revisar campos requeridos y formato |
| `401` | No autenticado | Verificar token JWT válido |
| `403` | No autorizado | Usuario debe tener permisos |
| `404` | No encontrado | Verificar que el endpoint existe |
| `429` | Demasiados intentos | Esperar antes de nuevo intento |

### 📝 Campos y Validaciones

**Contraseñas:**
- Longitud mínima: 8 caracteres
- Debe contener letras, números y símbolos
- No puede ser igual a contraseñas anteriores
- Validación de contraseñas comunes

**Verificaciones por Email:**
- Códigos expiran en 24 horas
- Máximo 5 intentos por código
- Un código por vez por tipo de verificación
- Emails deben ser únicos en el sistema

---
### 🧩 Módulo 3: Pacientes & Diagnósticos

## 🏥 Diagnósticos (/api/patients/diagnoses/)

### 🔗 Endpoints

| Método | Endpoint                                    | Descripción                               | Autenticación |
|-------:|---------------------------------------------|-------------------------------------------|---------------|
|    GET | `/api/patients/diagnoses/`                  | Listar diagnósticos                       | Requerida     |
|   POST | `/api/patients/diagnoses/create/`           | Crear diagnóstico                         | Requerida     |
|    PUT | `/api/patients/diagnoses/<int:pk>/edit/`    | Editar diagnóstico (completo)             | Requerida     |
|  PATCH | `/api/patients/diagnoses/<int:pk>/edit/`    | Editar diagnóstico (parcial)              | Requerida     |
| DELETE | `/api/patients/diagnoses/<int:pk>/delete/`  | Eliminar diagnóstico                       | Requerida     |
|    GET | `/api/patients/diagnoses/search/`           | Buscar diagnósticos                       | Requerida     |

> ℹ️ Notas:
> - Los diagnósticos son GLOBALES (no-tenant). No se usa `reflexo_id`.
> - Unicidad global por `code`.
> - Paginación disponible en el listado con `page` y `page_size`.
> - Búsqueda por `search` en el listado, o usar el endpoint `/diagnoses/search/`.

### 🧪 Ejemplos de Diagnósticos

#### 📋 Listar Diagnósticos

- Método: GET
- URL: `http://localhost:8000/api/patients/diagnoses/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Lumbalgia",
            "code": "DX001",
            "created_at": "2025-09-25T10:30:00Z",
            "updated_at": "2025-09-25T10:30:00Z"
        },
        {
            "id": 2,
            "name": "Cervicalgia",
            "code": "DX002",
            "created_at": "2025-09-25T10:35:00Z",
            "updated_at": "2025-09-25T10:35:00Z"
        }
    ]
}
```

#### ➕ Crear Diagnóstico

- Método: POST
- URL: `http://localhost:8000/api/patients/diagnoses/create/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

```json
{
    "name": "Lumbalgia",
    "code": "DX001"
}
```

- Respuesta 201 (ejemplo):

```json
{
    "id": 3,
    "name": "Lumbalgia",
    "code": "DX001",
    "created_at": "2025-09-25T11:00:00Z",
    "updated_at": "2025-09-25T11:00:00Z"
}
```

- Respuesta 400 Bad Request (datos inválidos):

```json
{
    "code": [
        "Un diagnóstico con este código ya existe."
    ]
}
```

#### ✏️ Editar Diagnóstico (PUT completo)

- Método: PUT
- URL: `http://localhost:8000/api/patients/diagnoses/3/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición se aplica al diagnóstico identificado por el `id` en la URL.

```json
{
    "name": "Lumbalgia crónica",
    "code": "DX001"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "id": 3,
    "name": "Lumbalgia crónica",
    "code": "DX001",
    "created_at": "2025-09-25T11:00:00Z",
    "updated_at": "2025-09-25T11:05:00Z"
}
```

#### 🩹 Editar Diagnóstico (PATCH parcial)

- Método: PATCH
- URL: `http://localhost:8000/api/patients/diagnoses/3/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición parcial se aplica al diagnóstico identificado por el `id` en la URL.

```json
{
    "name": "Lumbalgia aguda"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "id": 3,
    "name": "Lumbalgia aguda",
    "code": "DX001",
    "created_at": "2025-09-25T11:00:00Z",
    "updated_at": "2025-09-25T11:10:00Z"
}
```

#### 🗑️ Eliminar Diagnóstico

- Método: DELETE
- URL: `http://localhost:8000/api/patients/diagnoses/3/delete/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

> ℹ️ Nota: La eliminación se aplica al diagnóstico identificado por el `id` en la URL.

- Respuesta 200 (ejemplo):

```json
{
    "message": "Diagnóstico eliminado"
}
```

- Respuesta 404 Not Found:

```json
{
    "error": "Diagnóstico no encontrado"
}
```

> **Nota sobre eliminación:** Por defecto realiza un soft delete GLOBAL por `code` (marca `deleted_at` en TODOS los diagnósticos que comparten ese `code`, sin importar el tenant). Para eliminar definitivamente (hard delete), agrega `?hard=true` a la URL.

#### 🔍 Buscar Diagnósticos

- Método: GET
- URL: `http://localhost:8000/api/patients/diagnoses/search/?q=lumbalgia`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Lumbalgia",
            "code": "DX001",
            "created_at": "2025-09-25T10:30:00Z",
            "updated_at": "2025-09-25T10:30:00Z"
        }
    ]
}
```

> **Nota:** La búsqueda es parcial (substring) en `code` y `name` y no distingue mayúsculas/minúsculas. Parámetros: `q` (obligatorio), `page` (por defecto 1), `page_size` (por defecto 10).

### 📝 Campos del Modelo Diagnóstico

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | Integer | Auto | ID único del diagnóstico |
| `name` | String | Sí | Nombre del diagnóstico |
| `code` | String | Sí | Código único del diagnóstico |
| `created_at` | DateTime | Auto | Fecha de creación |
| `updated_at` | DateTime | Auto | Fecha de última actualización |

### 🚨 Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| `400` | Datos inválidos | Revisar formato JSON y campos requeridos |
| `401` | No autenticado | Verificar token JWT válido |
| `404` | Diagnóstico no encontrado | Verificar que el ID del diagnóstico existe |
| `500` | Error del servidor | Revisar logs del servidor |

### 📋 Validaciones

**Campos requeridos:**
- `name`: Nombre del diagnóstico
- `code`: Código único (no puede duplicarse)

**Reglas de negocio:**
- Los diagnósticos son globales (no multitenant)
- Unicidad global por `code`
- Soft delete por defecto (marca `deleted_at`)
- Hard delete disponible con `?hard=true`

---

## 👥 Pacientes (/api/patients/patients/)

### 🔗 Endpoints

| Método | Endpoint                                    | Descripción                               | Autenticación |
|-------:|---------------------------------------------|-------------------------------------------|---------------|
|    GET | `/api/patients/patients/`                  | Listar pacientes                          | Requerida     |
|   POST | `/api/patients/patients/create/`           | Crear paciente                            | Requerida     |
|    PUT | `/api/patients/patients/<int:pk>/edit/`    | Editar paciente (completo)                | Requerida     |
|  PATCH | `/api/patients/patients/<int:pk>/edit/`    | Editar paciente (parcial)                 | Requerida     |
| DELETE | `/api/patients/patients/<int:pk>/delete/`  | Eliminar paciente                          | Requerida     |
|    GET | `/api/patients/patients/search/`           | Buscar pacientes                          | Requerida     |

> ℹ️ Notas:
> - Los pacientes son multitenant (filtrados por `reflexo_id`).
> - Usuario con tenant: solo ve pacientes de su empresa.
> - Administrador global: puede ver todos los pacientes.
> - Paginación disponible en el listado con `page` y `per_page`.
> - Búsqueda por múltiples campos (nombre, apellidos, documento, email).

### 🧪 Ejemplos de Pacientes

#### 📋 Listar Pacientes

- Método: GET
- URL: `http://localhost:8000/api/patients/patients/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "count": 2,
    "num_pages": 1,
    "current_page": 1,
    "results": [
        {
            "id": 1,
            "document_number": "12345678",
            "paternal_lastname": "Pérez",
            "maternal_lastname": "García",
            "name": "Juan",
            "email": "juan.perez@example.com",
            "phone1": "999888777",
            "sex": "M",
            "address": "Av. Principal 123",
            "reflexo_id": 1,
            "created_at": "2025-09-25T10:30:00Z",
            "updated_at": "2025-09-25T10:30:00Z"
        }
    ]
}
```

#### ➕ Crear Paciente

- Método: POST
- URL: `http://localhost:8000/api/patients/patients/create/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

```json
{
    "document_number": "87654321",
    "paternal_lastname": "González",
    "maternal_lastname": "López",
    "name": "María",
    "email": "maria.gonzalez@example.com",
    "phone1": "987654321",
    "sex": "F",
    "address": "Calle Secundaria 456",
    "document_type_id": 1,
    "region_code": 1,
    "province_code": 101,
    "district_code": 10101,
    "ocupation": "Estudiante",
    "health_condition": "Sin antecedentes"
}
```

- Respuesta 201 (ejemplo):

```json
{
    "id": 2,
    "document_number": "87654321",
    "paternal_lastname": "González",
    "maternal_lastname": "López",
    "name": "María",
    "email": "maria.gonzalez@example.com",
    "phone1": "987654321",
    "sex": "F",
    "address": "Calle Secundaria 456",
    "reflexo_id": 1,
    "created_at": "2025-09-25T11:00:00Z",
    "updated_at": "2025-09-25T11:00:00Z"
}
```

- Respuesta 409 Conflict (paciente ya existe):

```json
{
    "message": "El paciente ya existe",
    "data": {
        "id": 2,
        "document_number": "87654321",
        "name": "María",
        "email": "maria.gonzalez@example.com"
    }
}
```

#### ✏️ Editar Paciente (PUT completo)

- Método: PUT
- URL: `http://localhost:8000/api/patients/patients/2/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición se aplica al paciente identificado por el `id` en la URL.

```json
{
    "document_number": "87654321",
    "paternal_lastname": "González",
    "maternal_lastname": "López",
    "name": "María Elena",
    "email": "maria.gonzalez@example.com",
    "phone1": "987654321",
    "sex": "F",
    "address": "Calle Secundaria 456",
    "document_type_id": 1,
    "region_code": 1,
    "province_code": 101,
    "district_code": 10101,
    "ocupation": "Estudiante",
    "health_condition": "Sin antecedentes"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "id": 2,
    "document_number": "87654321",
    "paternal_lastname": "González",
    "maternal_lastname": "López",
    "name": "María Elena",
    "email": "maria.gonzalez@example.com",
    "phone1": "987654321",
    "sex": "F",
    "address": "Calle Secundaria 456",
    "reflexo_id": 1,
    "created_at": "2025-09-25T11:00:00Z",
    "updated_at": "2025-09-25T11:05:00Z"
}
```

#### 🩹 Editar Paciente (PATCH parcial)

- Método: PATCH
- URL: `http://localhost:8000/api/patients/patients/2/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición parcial se aplica al paciente identificado por el `id` en la URL.

```json
{
    "phone1": "999111222",
    "address": "Nueva Dirección 789"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "id": 2,
    "document_number": "87654321",
    "paternal_lastname": "González",
    "maternal_lastname": "López",
    "name": "María Elena",
    "email": "maria.gonzalez@example.com",
    "phone1": "999111222",
    "sex": "F",
    "address": "Nueva Dirección 789",
    "reflexo_id": 1,
    "created_at": "2025-09-25T11:00:00Z",
    "updated_at": "2025-09-25T11:10:00Z"
}
```

#### 🗑️ Eliminar Paciente

- Método: DELETE
- URL: `http://localhost:8000/api/patients/patients/2/delete/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

> ℹ️ Nota: La eliminación se aplica al paciente identificado por el `id` en la URL.

- Respuesta 204 No Content (eliminación exitosa)

> **Nota sobre eliminación:** Por defecto realiza soft delete (marca `deleted_at`). Para eliminar definitivamente (hard delete), agrega `?hard=true` a la URL.

#### 🔍 Buscar Pacientes

- Método: GET
- URL: `http://localhost:8000/api/patients/patients/search/?q=maria&page=1`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "count": 1,
    "num_pages": 1,
    "current_page": 1,
    "results": [
        {
            "id": 2,
            "document_number": "87654321",
            "paternal_lastname": "González",
            "maternal_lastname": "López",
            "name": "María Elena",
            "email": "maria.gonzalez@example.com",
            "phone1": "999111222",
            "sex": "F",
            "address": "Nueva Dirección 789",
            "reflexo_id": 1,
            "created_at": "2025-09-25T11:00:00Z",
            "updated_at": "2025-09-25T11:10:00Z"
        }
    ]
}
```

> **Nota:** La búsqueda funciona por coincidencias parciales en nombre, apellidos, documento y email. Parámetros: `q` (obligatorio), `page` (por defecto 1), `per_page` (por defecto 10).

### 📝 Campos del Modelo Paciente

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | Integer | Auto | ID único del paciente |
| `document_number` | String | Sí | Número de documento único |
| `paternal_lastname` | String | Sí | Apellido paterno |
| `maternal_lastname` | String | No | Apellido materno |
| `name` | String | Sí | Nombre del paciente |
| `email` | String | Sí | Email único |
| `phone1` | String | No | Teléfono principal |
| `phone2` | String | No | Teléfono secundario |
| `sex` | String | No | Sexo (M/F) |
| `address` | String | No | Dirección |
| `document_type_id` | Integer | Sí | ID del tipo de documento |
| `region_code` | Integer | Sí | Código de región |
| `province_code` | Integer | Sí | Código de provincia |
| `district_code` | Integer | Sí | Código de distrito |
| `ocupation` | String | Sí | Ocupación |
| `health_condition` | String | Sí | Condición de salud |
| `reflexo_id` | Integer | Auto | ID de la empresa (tenant) |
| `created_at` | DateTime | Auto | Fecha de creación |
| `updated_at` | DateTime | Auto | Fecha de última actualización |
| `deleted_at` | DateTime | Auto | Fecha de eliminación (soft delete) |

### 🚨 Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| `400` | Datos inválidos | Revisar formato JSON y campos requeridos |
| `401` | No autenticado | Verificar token JWT válido |
| `404` | Paciente no encontrado | Verificar que el ID del paciente existe |
| `409` | Conflicto | El paciente ya existe (documento o email duplicado) |
| `500` | Error del servidor | Revisar logs del servidor |

### 📋 Validaciones

**Campos requeridos:**
- `document_number`: Número de documento único
- `paternal_lastname`: Apellido paterno
- `name`: Nombre del paciente
- `email`: Email único
- `document_type_id`: ID del tipo de documento
- `region_code`, `province_code`, `district_code`: Códigos de ubicación
- `ocupation`: Ocupación
- `health_condition`: Condición de salud

**Reglas de negocio:**
- Los pacientes son multitenant (filtrados por `reflexo_id`)
- Unicidad por `document_number` y `email`
- Soft delete por defecto (marca `deleted_at`)
- Hard delete disponible con `?hard=true`
- Validación de jerarquía geográfica (provincia pertenece a región, distrito pertenece a provincia)
---

## 📋 Historiales Médicos (/api/patients/medical-records/)

### 🔗 Endpoints

| Método | Endpoint                                          | Descripción                               | Autenticación |
|-------:|---------------------------------------------------|-------------------------------------------|---------------|
|    GET | `/api/patients/medical-records/`                 | Listar historiales médicos                | Requerida     |
|   POST | `/api/patients/medical-records/create/`          | Crear historial médico                    | Requerida     |
|    PUT | `/api/patients/medical-records/<int:pk>/edit/`   | Editar historial médico (completo)        | Requerida     |
|  PATCH | `/api/patients/medical-records/<int:pk>/edit/`   | Editar historial médico (parcial)         | Requerida     |
| DELETE | `/api/patients/medical-records/<int:pk>/delete/` | Eliminar historial médico                 | Requerida     |
|    GET | `/api/patients/medical-records/<int:pk>/`        | Ver historial médico específico           | Requerida     |

> ℹ️ Notas:
> - Los historiales médicos son multitenant (filtrados por `reflexo_id`).
> - Usuario con tenant: solo ve historiales de su empresa.
> - Administrador global: puede ver todos los historiales.
> - Paginación disponible en el listado con `page` y `page_size`.
> - Filtros disponibles: `patient_id`, `diagnose_id`, `status`, `date_from`, `date_to`.

### 🧪 Ejemplos de Historiales Médicos

#### 📋 Listar Historiales Médicos

- Método: GET
- URL: `http://localhost:8000/api/patients/medical-records/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "count": 2,
    "num_pages": 1,
    "current_page": 1,
    "results": [
        {
            "id": 1,
            "patient_id": 1,
            "diagnose_id": 1,
            "diagnosis_date": "2025-09-25",
            "notes": "Paciente presenta dolor lumbar",
            "symptoms": "Dolor en región lumbar",
            "treatment": "Reposo y medicación",
            "status": "active",
            "reflexo_id": 1,
            "created_at": "2025-09-25T10:30:00Z",
            "updated_at": "2025-09-25T10:30:00Z"
        }
    ]
}
```

#### ➕ Crear Historial Médico

- Método: POST
- URL: `http://localhost:8000/api/patients/medical-records/create/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

```json
{
    "patient_id": 2,
    "diagnose_id": 1,
    "diagnosis_date": "2025-09-25",
    "notes": "Control de seguimiento",
    "symptoms": "Dolor leve",
    "treatment": "Medicación antiinflamatoria",
    "status": "active"
}
```

- Respuesta 201 (ejemplo):

```json
{
    "id": 2,
    "patient_id": 2,
    "diagnose_id": 1,
    "diagnosis_date": "2025-09-25",
    "notes": "Control de seguimiento",
    "symptoms": "Dolor leve",
    "treatment": "Medicación antiinflamatoria",
    "status": "active",
    "reflexo_id": 1,
    "created_at": "2025-09-25T11:00:00Z",
    "updated_at": "2025-09-25T11:00:00Z"
}
```

- Respuesta 400 Bad Request (datos inválidos):

```json
{
    "non_field_errors": [
        "Paciente y diagnóstico pertenecen a diferentes empresas (tenant)."
    ]
}
```

#### ✏️ Editar Historial Médico (PUT completo)

- Método: PUT
- URL: `http://localhost:8000/api/patients/medical-records/2/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición se aplica al historial médico identificado por el `id` en la URL.

```json
{
    "patient_id": 2,
    "diagnose_id": 1,
    "diagnosis_date": "2025-09-25",
    "notes": "Control de seguimiento actualizado",
    "symptoms": "Dolor leve persistente",
    "treatment": "Medicación antiinflamatoria y fisioterapia",
    "status": "active"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "id": 2,
    "patient_id": 2,
    "diagnose_id": 1,
    "diagnosis_date": "2025-09-25",
    "notes": "Control de seguimiento actualizado",
    "symptoms": "Dolor leve persistente",
    "treatment": "Medicación antiinflamatoria y fisioterapia",
    "status": "active",
    "reflexo_id": 1,
    "created_at": "2025-09-25T11:00:00Z",
    "updated_at": "2025-09-25T11:05:00Z"
}
```

#### 🩹 Editar Historial Médico (PATCH parcial)

- Método: PATCH
- URL: `http://localhost:8000/api/patients/medical-records/2/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición parcial se aplica al historial médico identificado por el `id` en la URL.

```json
{
    "notes": "Control finalizado",
    "status": "completed"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "id": 2,
    "patient_id": 2,
    "diagnose_id": 1,
    "diagnosis_date": "2025-09-25",
    "notes": "Control finalizado",
    "symptoms": "Dolor leve persistente",
    "treatment": "Medicación antiinflamatoria y fisioterapia",
    "status": "completed",
    "reflexo_id": 1,
    "created_at": "2025-09-25T11:00:00Z",
    "updated_at": "2025-09-25T11:10:00Z"
}
```

#### 🗑️ Eliminar Historial Médico

- Método: DELETE
- URL: `http://localhost:8000/api/patients/medical-records/2/delete/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

> ℹ️ Nota: La eliminación se aplica al historial médico identificado por el `id` en la URL.

- Respuesta 204 No Content (eliminación exitosa)

> **Nota sobre eliminación:** Por defecto realiza soft delete (marca `deleted_at`). Para eliminar definitivamente (hard delete), agrega `?hard=true` a la URL.

#### 👁️ Ver Historial Médico Específico

- Método: GET
- URL: `http://localhost:8000/api/patients/medical-records/2/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "id": 2,
    "patient_id": 2,
    "diagnose_id": 1,
    "diagnosis_date": "2025-09-25",
    "notes": "Control finalizado",
    "symptoms": "Dolor leve persistente",
    "treatment": "Medicación antiinflamatoria y fisioterapia",
    "status": "completed",
    "reflexo_id": 1,
    "created_at": "2025-09-25T11:00:00Z",
    "updated_at": "2025-09-25T11:10:00Z"
}
```

### 📝 Campos del Modelo Historial Médico

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | Integer | Auto | ID único del historial médico |
| `patient_id` | Integer | Sí | ID del paciente |
| `diagnose_id` | Integer | Sí | ID del diagnóstico |
| `diagnosis_date` | Date | Sí | Fecha del diagnóstico |
| `notes` | String | No | Notas del historial |
| `symptoms` | String | No | Síntomas presentados |
| `treatment` | String | No | Tratamiento aplicado |
| `status` | String | No | Estado del historial |
| `reflexo_id` | Integer | Auto | ID de la empresa (tenant) |
| `created_at` | DateTime | Auto | Fecha de creación |
| `updated_at` | DateTime | Auto | Fecha de última actualización |
| `deleted_at` | DateTime | Auto | Fecha de eliminación (soft delete) |

### 🚨 Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| `400` | Datos inválidos | Revisar formato JSON y campos requeridos |
| `401` | No autenticado | Verificar token JWT válido |
| `404` | Historial médico no encontrado | Verificar que el ID del historial existe |
| `500` | Error del servidor | Revisar logs del servidor |

### 📋 Validaciones

**Campos requeridos:**
- `patient_id`: ID del paciente (debe existir y estar activo)
- `diagnose_id`: ID del diagnóstico (debe existir y estar activo)
- `diagnosis_date`: Fecha del diagnóstico

**Reglas de negocio:**
- Los historiales médicos son multitenant (filtrados por `reflexo_id`)
- El paciente y el diagnóstico deben pertenecer al mismo tenant
- Unicidad por trío: `(patient_id, diagnose_id, diagnosis_date)` debe ser único
- Soft delete por defecto (marca `deleted_at`)
- Hard delete disponible con `?hard=true`
- Validación de coherencia de tenant entre paciente y diagnóstico

---
## 🧩 Módulo 4: Terapeutas (/api/therapists/therapists/)

### 🔗 Endpoints

| Método | Endpoint                                    | Descripción                               | Autenticación |
|-------:|---------------------------------------------|-------------------------------------------|---------------|
|    GET | `/api/therapists/therapists/`               | Listar terapeutas                         | Requerida     |
|   POST | `/api/therapists/therapists/create/`        | Crear terapeuta                           | Requerida     |
|    PUT | `/api/therapists/therapists/<int:pk>/edit/` | Editar terapeuta (completo)               | Requerida     |
|  PATCH | `/api/therapists/therapists/<int:pk>/edit/` | Editar terapeuta (parcial)                | Requerida     |
| DELETE | `/api/therapists/therapists/<int:pk>/delete/` | Eliminar terapeuta (soft delete)         | Requerida     |
| DELETE | `/api/therapists/therapists/<int:pk>/hard-delete/` | Eliminar terapeuta (hard delete)        | Requerida     |
|    GET | `/api/therapists/therapists/<int:pk>/`      | Ver terapeuta específico                  | Requerida     |

> ℹ️ Notas:
> - Los terapeutas son multitenant (filtrados por `reflexo_id`).
> - Usuario con tenant: solo ve terapeutas de su empresa.
> - Administrador global: puede ver todos los terapeutas.
> - Filtros disponibles: `active=true|false`, `region`, `province`, `district`, `search`.
> - Búsqueda por múltiples campos (nombre, apellidos, documento, email, ubicación).

### 🧪 Ejemplos de Terapeutas

#### 📋 Listar Terapeutas

- Método: GET
- URL: `http://localhost:8000/api/therapists/therapists/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "reflexo_id": 1,
            "reflexo_name": "Reflexo A",
            "document_type": {
                "id": 1,
                "name": "DNI"
            },
            "document_number": "12345678",
            "last_name_paternal": "Pérez",
            "last_name_maternal": "García",
            "first_name": "Ana",
            "full_name": "Ana Pérez García",
            "birth_date": "1990-01-01",
            "gender": "F",
            "personal_reference": "REF001",
            "is_active": true,
            "phone": "999888777",
            "email": "ana.perez@gmail.com",
            "region": {
                "id": 30,
                "name": "Lima"
            },
            "province": {
                "id": 591,
                "name": "Lima"
            },
            "district": {
                "id": 5626,
                "name": "Miraflores"
            },
            "address": "Av. Principal 123",
            "profile_picture": "http://localhost:8000/media/therapists/photos/foto.jpg",
            "profile_picture_url": "/media/therapists/photos/foto.jpg",
            "created_at": "2025-09-25T10:30:00Z",
            "updated_at": "2025-09-25T10:30:00Z"
        }
    ]
}
```

#### ➕ Crear Terapeuta

- Método: POST
- URL: `http://localhost:8000/api/therapists/therapists/create/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

```json
{
    "document_type_id": 1,
    "document_number": "12345678",
    "last_name_paternal": "Pérez",
    "last_name_maternal": "García",
    "first_name": "Ana",
    "email": "ana.perez@gmail.com",
    "region_id": 30,
    "province_id": 591,
    "district_id": 5626,
    "phone": "999888777",
    "address": "Av. Principal 123",
    "birth_date": "1990-01-01",
    "gender": "F",
    "personal_reference": "REF001"
}
```

- Respuesta 201 (ejemplo):

```json
{
    "id": 2,
    "reflexo_id": 1,
    "reflexo_name": "Reflexo A",
    "document_type": {
        "id": 1,
        "name": "DNI"
    },
    "document_number": "12345678",
    "last_name_paternal": "Pérez",
    "last_name_maternal": "García",
    "first_name": "Ana",
    "full_name": "Ana Pérez García",
    "birth_date": "1990-01-01",
    "gender": "F",
    "personal_reference": "REF001",
    "is_active": true,
    "phone": "999888777",
    "email": "ana.perez@gmail.com",
    "region": {
        "id": 30,
        "name": "Lima"
    },
    "province": {
        "id": 591,
        "name": "Lima"
    },
    "district": {
        "id": 5626,
        "name": "Miraflores"
    },
    "address": "Av. Principal 123",
    "profile_picture": null,
    "profile_picture_url": null,
    "created_at": "2025-09-25T11:00:00Z",
    "updated_at": "2025-09-25T11:00:00Z"
}
```

#### ✏️ Editar Terapeuta (PUT completo)

- Método: PUT
- URL: `http://localhost:8000/api/therapists/therapists/2/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición se aplica al terapeuta identificado por el `id` en la URL.

```json
{
    "document_type_id": 1,
    "document_number": "12345678",
    "last_name_paternal": "Pérez",
    "last_name_maternal": "García",
    "first_name": "Ana María",
    "email": "ana.perez@gmail.com",
    "region_id": 30,
    "province_id": 591,
    "district_id": 5626,
    "phone": "999888777",
    "address": "Av. Principal 123",
    "birth_date": "1990-01-01",
    "gender": "F",
    "personal_reference": "REF001"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "id": 2,
    "reflexo_id": 1,
    "reflexo_name": "Reflexo A",
    "document_type": {
        "id": 1,
        "name": "DNI"
    },
    "document_number": "12345678",
    "last_name_paternal": "Pérez",
    "last_name_maternal": "García",
    "first_name": "Ana María",
    "full_name": "Ana María Pérez García",
    "birth_date": "1990-01-01",
    "gender": "F",
    "personal_reference": "REF001",
    "is_active": true,
    "phone": "999888777",
    "email": "ana.perez@gmail.com",
    "region": {
        "id": 30,
        "name": "Lima"
    },
    "province": {
        "id": 591,
        "name": "Lima"
    },
    "district": {
        "id": 5626,
        "name": "Miraflores"
    },
    "address": "Av. Principal 123",
    "profile_picture": null,
    "profile_picture_url": null,
    "created_at": "2025-09-25T11:00:00Z",
    "updated_at": "2025-09-25T11:05:00Z"
}
```

#### 🩹 Editar Terapeuta (PATCH parcial)

- Método: PATCH
- URL: `http://localhost:8000/api/therapists/therapists/2/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición parcial se aplica al terapeuta identificado por el `id` en la URL.

```json
{
    "phone": "999111222",
    "address": "Nueva Dirección 456"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "id": 2,
    "reflexo_id": 1,
    "reflexo_name": "Reflexo A",
    "document_type": {
        "id": 1,
        "name": "DNI"
    },
    "document_number": "12345678",
    "last_name_paternal": "Pérez",
    "last_name_maternal": "García",
    "first_name": "Ana María",
    "full_name": "Ana María Pérez García",
    "birth_date": "1990-01-01",
    "gender": "F",
    "personal_reference": "REF001",
    "is_active": true,
    "phone": "999111222",
    "email": "ana.perez@gmail.com",
    "region": {
        "id": 30,
        "name": "Lima"
    },
    "province": {
        "id": 591,
        "name": "Lima"
    },
    "district": {
        "id": 5626,
        "name": "Miraflores"
    },
    "address": "Nueva Dirección 456",
    "profile_picture": null,
    "profile_picture_url": null,
    "created_at": "2025-09-25T11:00:00Z",
    "updated_at": "2025-09-25T11:10:00Z"
}
```

#### 🗑️ Eliminar Terapeuta (Soft Delete)

- Método: DELETE
- URL: `http://localhost:8000/api/therapists/therapists/2/delete/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

> ℹ️ Nota: La eliminación se aplica al terapeuta identificado por el `id` en la URL.

- Respuesta 204 No Content (eliminación exitosa)

> **Nota:** Realiza soft delete (marca `deleted_at`). El terapeuta deja de aparecer en la API y en el Admin, pero la fila sigue en la base de datos.

#### 🗑️ Eliminar Terapeuta (Hard Delete)

- Método: DELETE
- URL: `http://localhost:8000/api/therapists/therapists/2/hard-delete/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

> ℹ️ Nota: La eliminación se aplica al terapeuta identificado por el `id` en la URL.

- Respuesta 204 No Content (eliminación exitosa)

> **Nota:** Realiza hard delete (eliminación definitiva). El terapeuta se elimina completamente de la base de datos y no aparece en ningún lado.

#### 👁️ Ver Terapeuta Específico

- Método: GET
- URL: `http://localhost:8000/api/therapists/therapists/2/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "id": 2,
    "reflexo_id": 1,
    "reflexo_name": "Reflexo A",
    "document_type": {
        "id": 1,
        "name": "DNI"
    },
    "document_number": "12345678",
    "last_name_paternal": "Pérez",
    "last_name_maternal": "García",
    "first_name": "Ana María",
    "full_name": "Ana María Pérez García",
    "birth_date": "1990-01-01",
    "gender": "F",
    "personal_reference": "REF001",
    "is_active": true,
    "phone": "999111222",
    "email": "ana.perez@gmail.com",
    "region": {
        "id": 30,
        "name": "Lima"
    },
    "province": {
        "id": 591,
        "name": "Lima"
    },
    "district": {
        "id": 5626,
        "name": "Miraflores"
    },
    "address": "Nueva Dirección 456",
    "profile_picture": null,
    "profile_picture_url": null,
    "created_at": "2025-09-25T11:00:00Z",
    "updated_at": "2025-09-25T11:10:00Z"
}
```

#### 📸 Gestión de Foto de Terapeuta

##### Subir Foto (POST)

- Método: POST
- URL: `http://localhost:8000/api/therapists/therapists/2/photo/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`
  - `Content-Type: multipart/form-data`
- Body → form-data
  - **Key:** `photo_file`
  - **Type:** Seleccionar `File` (no Text)
  - **Value:** Seleccionar el archivo de imagen desde tu computadora

- Respuesta 200 (ejemplo):

```json
{
    "message": "Foto actualizada",
    "therapist": {
        "id": 2,
        "profile_picture": "http://localhost:8000/media/therapists/photos/foto_actualizada.jpg",
        "profile_picture_url": "/media/therapists/photos/foto_actualizada.jpg"
    }
}
```

##### Eliminar Foto (DELETE)

- Método: DELETE
- URL: `http://localhost:8000/api/therapists/therapists/2/photo/delete/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "message": "Foto eliminada definitivamente",
    "therapist": {
        "id": 2,
        "profile_picture": null,
        "profile_picture_url": null
    }
}
```

### 📝 Campos del Modelo Terapeuta

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | Integer | Auto | ID único del terapeuta |
| `document_type_id` | Integer | Sí | ID del tipo de documento |
| `document_number` | String | Sí | Número de documento único |
| `last_name_paternal` | String | Sí | Apellido paterno |
| `last_name_maternal` | String | Sí | Apellido materno |
| `first_name` | String | Sí | Nombre del terapeuta |
| `email` | String | Sí | Email (debe terminar en @gmail.com) |
| `region_id` | Integer | Sí | ID de la región |
| `province_id` | Integer | Sí | ID de la provincia |
| `district_id` | Integer | Sí | ID del distrito |
| `phone` | String | No | Teléfono |
| `address` | String | No | Dirección |
| `birth_date` | Date | No | Fecha de nacimiento |
| `gender` | String | No | Género (M/F) |
| `personal_reference` | String | No | Referencia personal |
| `reflexo_id` | Integer | Auto | ID de la empresa (tenant) |
| `created_at` | DateTime | Auto | Fecha de creación |
| `updated_at` | DateTime | Auto | Fecha de última actualización |
| `deleted_at` | DateTime | Auto | Fecha de eliminación (soft delete) |

### 🚨 Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| `400` | Datos inválidos | Revisar formato JSON y campos requeridos |
| `401` | No autenticado | Verificar token JWT válido |
| `404` | Terapeuta no encontrado | Verificar que el ID del terapeuta existe |
| `500` | Error del servidor | Revisar logs del servidor |

### 📋 Validaciones

**Campos requeridos:**
- `document_type_id`: ID del tipo de documento
- `document_number`: Número de documento único
- `last_name_paternal`: Apellido paterno
- `last_name_maternal`: Apellido materno
- `first_name`: Nombre del terapeuta
- `email`: Email válido terminado en @gmail.com
- `region_id`, `province_id`, `district_id`: IDs de ubicación

**Reglas de negocio:**
- Los terapeutas son multitenant (filtrados por `reflexo_id`)
- Validación de jerarquía geográfica (provincia pertenece a región, distrito pertenece a provincia)
- El terapeuta debe tener al menos 18 años
- Email debe terminar en @gmail.com
- Soft delete por defecto (endpoint `/delete/`)
- Hard delete disponible con endpoint `/hard-delete/`
- Validación de documento según tipo (DNI: 8-9 dígitos, CE: máximo 12 dígitos, etc.)

---

## 🧩 Módulo 5: Citas & Estados (/api/appointments/)

### 📅 Citas Médicas (/api/appointments/appointments/)

#### 🔗 Endpoints

| Método | Endpoint                                    | Descripción                               | Autenticación |
|-------:|---------------------------------------------|-------------------------------------------|---------------|
|    GET | `/api/appointments/appointments/`           | Listar citas médicas                      | Requerida     |
|   POST | `/api/appointments/appointments/create/`    | Crear cita médica                         | Requerida     |
|    PUT | `/api/appointments/appointments/<int:pk>/edit/` | Editar cita médica (completo)         | Requerida     |
|  PATCH | `/api/appointments/appointments/<int:pk>/edit/` | Editar cita médica (parcial)          | Requerida     |
| DELETE | `/api/appointments/appointments/<int:pk>/delete/` | Eliminar cita médica                  | Requerida     |
|    GET | `/api/appointments/appointments/<int:pk>/` | Ver cita médica específica               | Requerida     |

#### 🎯 Acciones Personalizadas

| Método | Endpoint                                    | Descripción                               |
|-------:|---------------------------------------------|-------------------------------------------|
|    GET | `/api/appointments/appointments/completed/` | Listar citas completadas                  |
|    GET | `/api/appointments/appointments/pending/`   | Listar citas pendientes                   |
|    GET | `/api/appointments/appointments/by_date_range/` | Listar citas por rango de fechas      |
|    GET | `/api/appointments/appointments/check_availability/` | Verificar disponibilidad        |
|   POST | `/api/appointments/appointments/<int:pk>/cancel/` | Cancelar cita específica            |
|   POST | `/api/appointments/appointments/<int:pk>/reschedule/` | Reprogramar cita específica      |

> ℹ️ Notas:
> - Las citas son multitenant (filtradas por `reflexo_id`).
> - Usuario con tenant: solo ve citas de su empresa.
> - Administrador global: puede ver todas las citas.
> - Filtros disponibles: `appointment_date`, `appointment_status`, `patient`, `therapist`, `room`.
> - Búsqueda por: `ailments`, `diagnosis`, `observation`, `ticket_number`.
> - Ordenamiento por: `appointment_date`, `hour`, `created_at`, `updated_at`.

#### 🧪 Ejemplos de Citas Médicas

##### 📋 Listar Citas Médicas

- Método: GET
- URL: `http://localhost:8000/api/appointments/appointments/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "patient": {
                "id": 1,
                "name": "Juan",
                "paternal_lastname": "Pérez",
                "document_number": "12345678"
            },
            "therapist": {
                "id": 1,
                "first_name": "Ana",
                "last_name_paternal": "García",
                "document_number": "87654321"
            },
            "appointment_date": "2025-09-26",
            "hour": "10:00:00",
            "appointment_status": {
                "id": 1,
                "name": "Programada"
            },
            "appointment_type": "Consulta",
            "room": "Consultorio 1",
            "ailments": "Dolor lumbar",
            "diagnosis": "Lumbalgia",
            "observation": "Paciente refiere dolor moderado",
            "reflexo_id": 1,
            "created_at": "2025-09-25T10:30:00Z",
            "updated_at": "2025-09-25T10:30:00Z"
        }
    ]
}
```

##### ➕ Crear Cita Médica

- Método: POST
- URL: `http://localhost:8000/api/appointments/appointments/create/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

```json
{
    "patient": 2,
    "therapist": 1,
    "appointment_date": "2025-09-27",
    "hour": "14:00",
    "appointment_status": 4,
    "appointment_type": "Consulta",
    "room": "Consultorio 2",
    "ailments": "Dolor cervical",
    "diagnosis": "Cervicalgia",
    "observation": "Primera consulta"
}
```

- Respuesta 201 (ejemplo):

```json
{
    "id": 2,
    "patient": {
        "id": 2,
        "name": "María",
        "paternal_lastname": "González",
        "document_number": "87654321"
    },
    "therapist": {
        "id": 1,
        "first_name": "Ana",
        "last_name_paternal": "García",
        "document_number": "87654321"
    },
    "appointment_date": "2025-09-27",
    "hour": "14:00:00",
    "appointment_status": {
        "id": 1,
        "name": "Programada"
    },
    "appointment_type": "Consulta",
    "room": "Consultorio 2",
    "ailments": "Dolor cervical",
    "diagnosis": "Cervicalgia",
    "observation": "Primera consulta",
    "reflexo_id": 1,
    "created_at": "2025-09-25T11:00:00Z",
    "updated_at": "2025-09-25T11:00:00Z"
}
```

##### ✏️ Editar Cita Médica (PUT completo)

- Método: PUT
- URL: `http://localhost:8000/api/appointments/appointments/2/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición se aplica a la cita identificada por el `id` en la URL.

```json
{
    "patient": 2,
    "therapist": 1,
    "appointment_date": "2025-09-27",
    "hour": "15:00",
    "appointment_status": 2,
    "appointment_type": "Seguimiento",
    "room": "Consultorio 1",
    "ailments": "Dolor cervical mejorado",
    "diagnosis": "Cervicalgia en recuperación",
    "observation": "Seguimiento de tratamiento"
}
```

##### 🩹 Editar Cita Médica (PATCH parcial)

- Método: PATCH
- URL: `http://localhost:8000/api/appointments/appointments/2/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición parcial se aplica a la cita identificada por el `id` en la URL.

```json
{
    "hour": "16:00",
    "observation": "Cambio de horario por solicitud del paciente"
}
```

##### 🗑️ Eliminar Cita Médica

- Método: DELETE
- URL: `http://localhost:8000/api/appointments/appointments/2/delete/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

> ℹ️ Nota: La eliminación se aplica a la cita identificada por el `id` en la URL.

- Respuesta 204 No Content (eliminación exitosa)

> **Nota sobre eliminación:** Por defecto realiza soft delete (marca `deleted_at`). Para eliminar definitivamente (hard delete), agrega `?hard=true` a la URL.

##### 👁️ Ver Cita Médica Específica

- Método: GET
- URL: `http://localhost:8000/api/appointments/appointments/2/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "id": 2,
    "patient": {
        "id": 2,
        "name": "María",
        "paternal_lastname": "González",
        "document_number": "87654321"
    },
    "therapist": {
        "id": 1,
        "first_name": "Ana",
        "last_name_paternal": "García",
        "document_number": "87654321"
    },
    "appointment_date": "2025-09-27",
    "hour": "16:00:00",
    "appointment_status": {
        "id": 1,
        "name": "Programada"
    },
    "appointment_type": "Seguimiento",
    "room": "Consultorio 1",
    "ailments": "Dolor cervical mejorado",
    "diagnosis": "Cervicalgia en recuperación",
    "observation": "Cambio de horario por solicitud del paciente",
    "reflexo_id": 1,
    "created_at": "2025-09-25T11:00:00Z",
    "updated_at": "2025-09-25T11:30:00Z"
}
```

##### 📋 Listar Citas Completadas

- Método: GET
- URL: `http://localhost:8000/api/appointments/appointments/completed/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

##### 📋 Listar Citas Pendientes

- Método: GET
- URL: `http://localhost:8000/api/appointments/appointments/pending/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

##### 📅 Citas por Rango de Fechas

- Método: GET
- URL: `http://localhost:8000/api/appointments/appointments/by_date_range/?start_date=2025-09-26&end_date=2025-09-30`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

##### ✅ Verificar Disponibilidad

- Método: GET
- URL: `http://localhost:8000/api/appointments/appointments/check_availability/?date=2025-09-27&hour=14:00`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

##### ❌ Cancelar Cita

- Método: POST
- URL: `http://localhost:8000/api/appointments/appointments/2/cancel/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

##### 📅 Reprogramar Cita

- Método: POST
- URL: `http://localhost:8000/api/appointments/appointments/2/reschedule/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

```json
{
    "appointment_date": "2025-09-28",
    "hour": "10:00",
    "reason": "Cambio solicitado por el paciente"
}
```

#### 📝 Campos del Modelo Cita Médica

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | Integer | Auto | ID único de la cita |
| `patient` | Integer | Sí | ID del paciente |
| `therapist` | Integer | Sí | ID del terapeuta |
| `appointment_date` | Date | Sí | Fecha de la cita |
| `hour` | Time | Sí | Hora de la cita |
| `appointment_status` | Integer | Sí | ID del estado de la cita |
| `appointment_type` | String | No | Tipo de cita |
| `room` | String | No | Sala/consultorio |
| `ailments` | String | No | Padecimientos del paciente |
| `diagnosis` | String | No | Diagnóstico |
| `observation` | String | No | Observaciones |
| `reflexo_id` | Integer | Auto | ID de la empresa (tenant) |
| `created_at` | DateTime | Auto | Fecha de creación |
| `updated_at` | DateTime | Auto | Fecha de última actualización |
| `deleted_at` | DateTime | Auto | Fecha de eliminación (soft delete) |

#### 🚨 Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| `400` | Datos inválidos | Revisar formato JSON y campos requeridos |
| `401` | No autenticado | Verificar token JWT válido |
| `404` | Cita no encontrada | Verificar que el ID de la cita existe |
| `409` | Conflicto | Verificar disponibilidad del terapeuta y sala |
| `500` | Error del servidor | Revisar logs del servidor |

#### 📋 Validaciones

**Campos requeridos:**
- `patient`: ID del paciente (debe existir y estar activo)
- `therapist`: ID del terapeuta (debe existir y estar activo)
- `appointment_date`: Fecha de la cita
- `hour`: Hora de la cita
- `appointment_status`: ID del estado de la cita (debe existir)

**Reglas de negocio:**
- Las citas son multitenant (filtradas por `reflexo_id`)
- El paciente y terapeuta deben pertenecer al mismo tenant
- Validación de disponibilidad del terapeuta y sala
- No se pueden crear citas en fechas pasadas
- Soft delete por defecto (marca `deleted_at`)
- Hard delete disponible con `?hard=true`

---

### 📊 Estados de Citas (/api/appointments/appointment-statuses/)

#### 🔗 Endpoints

| Método | Endpoint                                          | Descripción                               | Autenticación |
|-------:|---------------------------------------------------|-------------------------------------------|---------------|
|    GET | `/api/appointments/appointment-statuses/`        | Listar estados de citas                   | Requerida     |
|   POST | `/api/appointments/appointment-statuses/create/` | Crear estado de cita                      | Requerida     |
|    PUT | `/api/appointments/appointment-statuses/<int:pk>/edit/` | Editar estado (completo)          | Requerida     |
|  PATCH | `/api/appointments/appointment-statuses/<int:pk>/edit/` | Editar estado (parcial)           | Requerida     |
| DELETE | `/api/appointments/appointment-statuses/<int:pk>/delete/` | Eliminar estado              | Requerida     |
|    GET | `/api/appointments/appointment-statuses/<int:pk>/` | Ver estado específico             | Requerida     |

#### 🎯 Acciones Personalizadas

| Método | Endpoint                                          | Descripción                               |
|-------:|---------------------------------------------------|-------------------------------------------|
|    GET | `/api/appointments/appointment-statuses/active/`  | Listar estados activos                    |
|   POST | `/api/appointments/appointment-statuses/<int:pk>/activate/` | Activar estado específico        |
|   POST | `/api/appointments/appointment-statuses/<int:pk>/deactivate/` | Desactivar estado específico   |
|    GET | `/api/appointments/appointment-statuses/<int:pk>/appointments/` | Ver citas con este estado  |

> ℹ️ Notas:
> - Los estados de citas son **GLOBALES** (no multitenant).
> - Todos los usuarios autenticados pueden ver todos los estados.
> - Filtros disponibles: `name`.
> - Búsqueda por: `name`, `description`.
> - Ordenamiento por: `name`, `created_at`, `updated_at`.

#### 🧪 Ejemplos de Estados de Citas

##### 📋 Listar Estados de Citas

- Método: GET
- URL: `http://localhost:8000/api/appointments/appointment-statuses/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "count": 4,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Programada",
            "description": "Cita programada y confirmada",
            "created_at": "2025-09-25T10:30:00Z",
            "updated_at": "2025-09-25T10:30:00Z"
        },
        {
            "id": 2,
            "name": "En Progreso",
            "description": "Cita en curso de realización",
            "created_at": "2025-09-25T10:30:00Z",
            "updated_at": "2025-09-25T10:30:00Z"
        },
        {
            "id": 3,
            "name": "Completada",
            "description": "Cita finalizada exitosamente",
            "created_at": "2025-09-25T10:30:00Z",
            "updated_at": "2025-09-25T10:30:00Z"
        },
        {
            "id": 4,
            "name": "Cancelada",
            "description": "Cita cancelada",
            "created_at": "2025-09-25T10:30:00Z",
            "updated_at": "2025-09-25T10:30:00Z"
        }
    ]
}
```

##### ➕ Crear Estado de Cita

- Método: POST
- URL: `http://localhost:8000/api/appointments/appointment-statuses/create/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

```json
{
    "name": "Reagendada",
    "description": "Cita reagendada por solicitud del paciente"
}
```

- Respuesta 201 (ejemplo):

```json
{
    "id": 5,
    "name": "Reagendada",
    "description": "Cita reagendada por solicitud del paciente",
    "created_at": "2025-09-25T11:00:00Z",
    "updated_at": "2025-09-25T11:00:00Z"
}
```

##### ✏️ Editar Estado de Cita (PUT completo)

- Método: PUT
- URL: `http://localhost:8000/api/appointments/appointment-statuses/5/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición se aplica al estado identificado por el `id` en la URL.

```json
{
    "name": "Reagendada",
    "description": "Cita reagendada por solicitud del paciente o terapeuta"
}
```

##### 🩹 Editar Estado de Cita (PATCH parcial)

- Método: PATCH
- URL: `http://localhost:8000/api/appointments/appointment-statuses/5/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición parcial se aplica al estado identificado por el `id` en la URL.

```json
{
    "description": "Cita reagendada por cualquier motivo válido"
}
```

##### 🗑️ Eliminar Estado de Cita

- Método: DELETE
- URL: `http://localhost:8000/api/appointments/appointment-statuses/5/delete/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

**¿Para qué sirve?**
- **Soft Delete por defecto**: Marca `deleted_at` pero mantiene el registro
- **Hard Delete opcional**: Elimina definitivamente con `?hard=true`
- **Recuperable**: Los soft deletes se pueden restaurar con `/activate/`

**Parámetros opcionales:**
- `?hard=true` - Eliminación definitiva (no recuperable)

**Ejemplos:**

**Soft Delete (por defecto):**
```bash
DELETE /api/appointments/appointment-statuses/5/delete/
```

**Hard Delete (eliminación definitiva):**
```bash
DELETE /api/appointments/appointment-statuses/5/delete/?hard=true
```

**Respuestas:**
- `204 No Content` - Eliminación exitosa (soft o hard delete)

> ℹ️ Nota: La eliminación se aplica al estado identificado por el `id` en la URL.

##### 👁️ Ver Estado de Cita Específico

- Método: GET
- URL: `http://localhost:8000/api/appointments/appointment-statuses/5/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "id": 5,
    "name": "Reagendada",
    "description": "Cita reagendada por cualquier motivo válido",
    "created_at": "2025-09-25T11:00:00Z",
    "updated_at": "2025-09-25T11:15:00Z"
}
```

##### ✅ Listar Estados Activos

- Método: GET
- URL: `http://localhost:8000/api/appointments/appointment-statuses/active/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

**¿Para qué sirve?**
- Obtiene **solo los estados disponibles** para usar en citas nuevas
- Excluye estados eliminados (soft delete)
- Útil para **dropdowns/selects** en el frontend
- **Ejemplo de uso**: Al crear una cita, solo mostrar estados válidos

**Respuesta 200 (ejemplo):**
```json
[
    {
        "id": 2,
        "name": "Completa",
        "description": "Cita finalizada exitosamente",
        "appointments_count": 5,
        "created_at": "2025-09-25T10:30:00Z",
        "updated_at": "2025-09-25T10:30:00Z",
        "deleted_at": null
    },
    {
        "id": 4,
        "name": "En espera",
        "description": "Cita programada y confirmada",
        "appointments_count": 12,
        "created_at": "2025-09-25T10:30:00Z",
        "updated_at": "2025-09-25T10:30:00Z",
        "deleted_at": null
    },
    {
        "id": 5,
        "name": "Cancelada",
        "description": "Cita cancelada",
        "appointments_count": 3,
        "created_at": "2025-09-25T10:30:00Z",
        "updated_at": "2025-09-25T10:30:00Z",
        "deleted_at": null
    }
]
```

##### 🔄 Activar Estado

- Método: POST
- URL: `http://localhost:8000/api/appointments/appointment-statuses/5/activate/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

**¿Para qué sirve?**
- **Restaura un estado eliminado** (soft delete → activo)
- Útil cuando se eliminó por error un estado
- **No crea nuevo**, solo restaura el existente
- **Ejemplo de uso**: "Oops, eliminé 'En espera' por error, lo reactivo"

**Respuesta 200 (ejemplo):**
```json
{
    "id": 5,
    "name": "Cancelada",
    "description": "Cita cancelada",
    "appointments_count": 3,
    "created_at": "2025-09-25T10:30:00Z",
    "updated_at": "2025-09-26T12:00:00Z",
    "deleted_at": null
}
```

**Respuesta 404 Not Found:**
```json
{
    "detail": "No encontrado."
}
```

##### ⏸️ Desactivar Estado

- Método: POST
- URL: `http://localhost:8000/api/appointments/appointment-statuses/5/deactivate/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

**¿Para qué sirve?**
- **Elimina temporalmente** un estado (soft delete)
- No se puede usar en nuevas citas
- Las citas existentes **mantienen** el estado
- **Ejemplo de uso**: "Ya no usamos 'Pospuesta', lo desactivo"

**Respuesta 200 (ejemplo):**
```json
{
    "id": 5,
    "name": "Cancelada",
    "description": "Cita cancelada",
    "appointments_count": 3,
    "created_at": "2025-09-25T10:30:00Z",
    "updated_at": "2025-09-26T12:00:00Z",
    "deleted_at": "2025-09-26T12:00:00Z"
}
```

**Respuesta 404 Not Found:**
```json
{
    "detail": "No encontrado."
}
```

##### 📋 Ver Citas con Estado Específico

- Método: GET
- URL: `http://localhost:8000/api/appointments/appointment-statuses/3/appointments/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

**¿Para qué sirve?**
- Muestra **todas las citas** que tienen un estado específico
- Útil para **reportes y análisis**
- **Ejemplo de uso**: "¿Cuántas citas están 'En espera'?"

**Respuesta 200 (ejemplo):**
```json
{
    "status": {
        "id": 4,
        "name": "En espera",
        "description": "Cita programada y confirmada"
    },
    "appointments": [
        {
            "id": 1,
            "patient_name": "Juan Pérez",
            "therapist_name": "Ana García",
            "appointment_date": "2025-09-27",
            "hour": "10:00:00",
            "appointment_type": "Consulta",
            "room": "Consultorio 1",
            "created_at": "2025-09-25T10:30:00Z",
            "updated_at": "2025-09-25T10:30:00Z"
        },
        {
            "id": 3,
            "patient_name": "María González",
            "therapist_name": "Carlos López",
            "appointment_date": "2025-09-28",
            "hour": "14:30:00",
            "appointment_type": "Seguimiento",
            "room": "Consultorio 2",
            "created_at": "2025-09-25T11:15:00Z",
            "updated_at": "2025-09-25T11:15:00Z"
        }
    ],
    "count": 2
}
```

**Respuesta 404 Not Found:**
```json
{
    "detail": "No encontrado."
}
```

### 🔍 **Nota importante sobre Soft Delete**

**¿Por qué veo el registro en la base de datos después de eliminarlo?**

- **Soft Delete**: El endpoint `/delete/` hace **soft delete** por defecto
- **¿Qué hace?**: Marca `deleted_at` con timestamp, pero **NO elimina** el registro
- **¿Por qué?**: Para poder **recuperar** si fue un error y mantener **auditoría**

**¿Cómo verificar que funcionó?**
```bash
# Estados activos (aparecen en API)
GET /api/appointments/appointment-statuses/active/

# Estados eliminados (NO aparecen en API)
# El registro sigue en BD pero con deleted_at != NULL
```

**¿Cómo hacer Hard Delete (eliminación definitiva)?**
```bash
DELETE /api/appointments/appointment-statuses/6/delete/?hard=true
```

**Ejemplo de uso:**
```json
DELETE /api/appointments/appointment-statuses/6/delete/?hard=true
```

**Respuesta:**
- `204 No Content` - Eliminación exitosa
- El registro se **elimina completamente** de la base de datos
- **No se puede recuperar** después del hard delete

**¿Cómo restaurar un estado eliminado?**
```bash
POST /api/appointments/appointment-statuses/6/activate/
```

#### 📝 Campos del Modelo Estado de Cita

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | Integer | Auto | ID único del estado |
| `name` | String | Sí | Nombre del estado |
| `description` | String | No | Descripción del estado |
| `created_at` | DateTime | Auto | Fecha de creación |
| `updated_at` | DateTime | Auto | Fecha de última actualización |

#### 🚨 Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| `400` | Datos inválidos | Revisar formato JSON y campos requeridos |
| `401` | No autenticado | Verificar token JWT válido |
| `404` | Estado no encontrado | Verificar que el ID del estado existe |
| `409` | Conflicto | El nombre del estado ya existe |
| `500` | Error del servidor | Revisar logs del servidor |

#### 📋 Validaciones

**Campos requeridos:**
- `name`: Nombre del estado (debe ser único)

**Reglas de negocio:**
- Los estados son globales (no multitenant)
- Unicidad global por `name`
- Soft delete por defecto (marca `deleted_at`)
- Hard delete disponible con `?hard=true`

---

### 🎫 Tickets de Citas (/api/appointments/tickets/)

#### 🚀 **Guía Rápida de Parámetros**

**⚠️ IMPORTANTE:** Algunos endpoints requieren parámetros específicos:

| Endpoint | Parámetro Requerido | Ejemplo |
|----------|-------------------|---------|
| `by_ticket_number` | `ticket_number` | `?ticket_number=TKT-001` |
| `by_number` | `number` | `?number=TKT-001` |
| `by_payment_method` | `payment_method` o `method` | `?payment_method=cash` |

**❌ Errores comunes:**
- Usar `?number=TKT-001` en `by_ticket_number` → Error 400
- No usar parámetros en `by_payment_method` → Error 400

#### 🔗 Endpoints

| Método | Endpoint                                    | Descripción                               | Autenticación |
|-------:|---------------------------------------------|-------------------------------------------|---------------|
|    GET | `/api/appointments/tickets/`                | Listar tickets de citas                   | Requerida     |
|   POST | `/api/appointments/tickets/create/`         | Crear ticket de cita                      | Requerida     |
|    PUT | `/api/appointments/tickets/<int:pk>/edit/` | Editar ticket (completo)                  | Requerida     |
|  PATCH | `/api/appointments/tickets/<int:pk>/edit/` | Editar ticket (parcial)                   | Requerida     |
| DELETE | `/api/appointments/tickets/<int:pk>/delete/` | Eliminar ticket                       | Requerida     |
|    GET | `/api/appointments/tickets/<int:pk>/`      | Ver ticket específico                     | Requerida     |

#### 🎯 Acciones Personalizadas

| Método | Endpoint                                    | Descripción                               | Parámetros Requeridos |
|-------:|---------------------------------------------|-------------------------------------------|----------------------|
|    GET | `/api/appointments/tickets/paid/`           | Listar tickets pagados                    | Ninguno              |
|    GET | `/api/appointments/tickets/pending/`        | Listar tickets pendientes                 | Ninguno              |
|    GET | `/api/appointments/tickets/cancelled/`      | Listar tickets cancelados                 | Ninguno              |
|   POST | `/api/appointments/tickets/<int:pk>/mark_as_paid/` | Marcar ticket como pagado       | Ninguno              |
|   POST | `/api/appointments/tickets/<int:pk>/mark_paid/` | Alias para marcar como pagado     | Ninguno              |
|   POST | `/api/appointments/tickets/<int:pk>/mark_as_cancelled/` | Marcar ticket como cancelado | Ninguno              |
|   POST | `/api/appointments/tickets/<int:pk>/cancel/` | Alias para cancelar ticket         | Ninguno              |
|    GET | `/api/appointments/tickets/by_payment_method/` | Tickets por método de pago | `payment_method` o `method` |
|    GET | `/api/appointments/tickets/by_ticket_number/` | Buscar ticket por número         | `ticket_number`      |
|    GET | `/api/appointments/tickets/by_number/`     | Alias para buscar por número             | `number`             |
|    GET | `/api/appointments/tickets/statistics/`    | Estadísticas de tickets                   | Ninguno              |

> ℹ️ Notas:
> - Los tickets son multitenant (filtrados por `reflexo_id`).
> - Usuario con tenant: solo ve tickets de su empresa.
> - Administrador global: puede ver todos los tickets.
> - Filtros disponibles: `ticket_number`, `payment_method`, `status`, `is_active`.
> - Búsqueda por: `ticket_number`, `description`.
> - Ordenamiento por: `payment_date`, `amount`, `created_at`, `updated_at`.
> - ⚠️ **NOTA IMPORTANTE**: El endpoint `POST /tickets/create/` está **EN DESUSO**. Los tickets se crean automáticamente al crear una cita.

#### 🧪 Ejemplos de Tickets

##### 📋 Listar Tickets

- Método: GET
- URL: `http://localhost:8000/api/appointments/tickets/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "ticket_number": "TKT-001",
            "appointment": {
                "id": 1,
                "patient": {
                    "id": 1,
                    "name": "Juan",
                    "paternal_lastname": "Pérez"
                },
                "therapist": {
                    "id": 1,
                    "first_name": "Ana",
                    "last_name_paternal": "García"
                },
                "appointment_date": "2025-09-26",
                "hour": "10:00:00"
            },
            "amount": 150.00,
            "payment_method": "cash",
            "payment_date": "2025-09-26T10:30:00Z",
            "status": "paid",
            "description": "Consulta de fisioterapia",
            "is_active": true,
            "reflexo_id": 1,
            "created_at": "2025-09-25T10:30:00Z",
            "updated_at": "2025-09-25T10:30:00Z"
        }
    ]
}
```

##### ⚠️ Crear Ticket (EN DESUSO)

> **IMPORTANTE**: Este endpoint está **DEPRECADO/EN DESUSO**. Los tickets se crean automáticamente al crear una cita.

- Método: POST
- URL: `http://localhost:8000/api/appointments/tickets/create/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

```json
{
    "appointment": 1,
    "amount": 150.00,
    "payment_method": "cash"
}
```

> **Nota**: No es necesario ni recomendado crear tickets manualmente vía API.

##### ✏️ Editar Ticket (PUT completo)

- Método: PUT
- URL: `http://localhost:8000/api/appointments/tickets/1/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición se aplica al ticket identificado por el `id` en la URL.

```json
{
    "amount": 180.00,
    "payment_method": "card",
    "status": "paid",
    "description": "Consulta de fisioterapia - Actualizada"
}
```

##### 🩹 Editar Ticket (PATCH parcial)

- Método: PATCH
- URL: `http://localhost:8000/api/appointments/tickets/1/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición parcial se aplica al ticket identificado por el `id` en la URL.

```json
{
    "status": "paid"
}
```

##### 🗑️ Eliminar Ticket

- Método: DELETE
- URL: `http://localhost:8000/api/appointments/tickets/1/delete/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

> ℹ️ Nota: La eliminación se aplica al ticket identificado por el `id` en la URL.

- Respuesta 204 No Content (eliminación exitosa)

> **Nota sobre eliminación:** Realiza eliminación DEFINITIVA (hard delete) GLOBAL del ticket. El registro se elimina de la base de datos y no aparece en la API ni en el panel de Django Admin.

##### 👁️ Ver Ticket Específico

- Método: GET
- URL: `http://localhost:8000/api/appointments/tickets/1/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "id": 1,
    "ticket_number": "TKT-001",
    "appointment": {
        "id": 1,
        "patient": {
            "id": 1,
            "name": "Juan",
            "paternal_lastname": "Pérez"
        },
        "therapist": {
            "id": 1,
            "first_name": "Ana",
            "last_name_paternal": "García"
        },
        "appointment_date": "2025-09-26",
        "hour": "10:00:00"
    },
    "amount": 180.00,
    "payment_method": "card",
    "payment_date": "2025-09-26T10:30:00Z",
    "status": "paid",
    "description": "Consulta de fisioterapia - Actualizada",
    "is_active": true,
    "reflexo_id": 1,
    "created_at": "2025-09-25T10:30:00Z",
    "updated_at": "2025-09-25T11:15:00Z"
}
```

##### 💰 Listar Tickets Pagados

- Método: GET
- URL: `http://localhost:8000/api/appointments/tickets/paid/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

**¿Para qué sirve?**
- Obtiene **solo los tickets con estado 'paid'**
- Útil para reportes de ingresos
- **Ejemplo de uso**: "¿Cuánto hemos cobrado hoy?"

**Respuesta 200 (ejemplo):**
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "ticket_number": "TKT-001",
            "amount": 150.00,
            "payment_method": "cash",
            "status": "paid",
            "payment_date": "2025-09-26T10:30:00Z"
        }
    ]
}
```

##### ⏳ Listar Tickets Pendientes

- Método: GET
- URL: `http://localhost:8000/api/appointments/tickets/pending/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

**¿Para qué sirve?**
- Obtiene **solo los tickets con estado 'pending'**
- Útil para seguimiento de cobros
- **Ejemplo de uso**: "¿Qué tickets faltan por cobrar?"

##### ❌ Listar Tickets Cancelados

- Método: GET
- URL: `http://localhost:8000/api/appointments/tickets/cancelled/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

**¿Para qué sirve?**
- Obtiene **solo los tickets con estado 'cancelled'**
- Útil para auditoría y reportes
- **Ejemplo de uso**: "¿Cuántos tickets se cancelaron?"

##### ✅ Marcar Ticket como Pagado

- Método: POST
- URL: `http://localhost:8000/api/appointments/tickets/1/mark_as_paid/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

**¿Para qué sirve?**
- Cambia el estado del ticket de `pending` a `paid`
- Actualiza automáticamente `payment_date`
- **Ejemplo de uso**: "El paciente ya pagó, marco el ticket como pagado"

**Respuesta 200 (ejemplo):**
```json
{
    "message": "Ticket marcado como pagado",
    "ticket": {
        "id": 1,
        "ticket_number": "TKT-001",
        "status": "paid",
        "payment_date": "2025-09-26T12:00:00Z"
    }
}
```

##### 💳 Marcar Ticket como Pagado (Alias)

- Método: POST
- URL: `http://localhost:8000/api/appointments/tickets/1/mark_paid/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

**Nota:** Es un alias de `mark_as_paid`, funciona exactamente igual.

##### 🚫 Marcar Ticket como Cancelado

- Método: POST
- URL: `http://localhost:8000/api/appointments/tickets/1/mark_as_cancelled/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

**¿Para qué sirve?**
- Cambia el estado del ticket a `cancelled`
- **Ejemplo de uso**: "El paciente canceló la cita, cancelo el ticket"

**Respuesta 200 (ejemplo):**
```json
{
    "message": "Ticket marcado como cancelado",
    "ticket": {
        "id": 1,
        "ticket_number": "TKT-001",
        "status": "cancelled"
    }
}
```

##### ❌ Cancelar Ticket (Alias)

- Método: POST
- URL: `http://localhost:8000/api/appointments/tickets/1/cancel/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

**Nota:** Es un alias de `mark_as_cancelled`, funciona exactamente igual.

##### 💳 Tickets por Método de Pago

- Método: GET
- URL: `http://localhost:8000/api/appointments/tickets/by_payment_method/?payment_method=cash`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

**Parámetros requeridos:**
- `payment_method` - Método de pago a filtrar (cash, card, transfer)
- `method` - Alias de `payment_method`

**Ejemplos de uso:**
```bash
# Usando payment_method
GET /api/appointments/tickets/by_payment_method/?payment_method=cash

# Usando alias method
GET /api/appointments/tickets/by_payment_method/?method=card

# Métodos válidos: cash, card, transfer
GET /api/appointments/tickets/by_payment_method/?payment_method=transfer
```

**Respuesta 400 Bad Request (sin parámetro):**
```json
{
    "error": "Se requiere payment_method (o alias: method)"
}
```

##### 🔍 Buscar Ticket por Número

- Método: GET
- URL: `http://localhost:8000/api/appointments/tickets/by_ticket_number/?ticket_number=TKT-001`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

**Parámetros requeridos:**
- `ticket_number` - Número del ticket a buscar

**Ejemplo de uso:**
```bash
GET /api/appointments/tickets/by_ticket_number/?ticket_number=TKT-001
```

##### 🔍 Buscar Ticket por Número (Alias)

- Método: GET
- URL: `http://localhost:8000/api/appointments/tickets/by_number/?number=TKT-001`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

**Parámetros requeridos:**
- `number` - Número del ticket a buscar (alias de `ticket_number`)

**Ejemplo de uso:**
```bash
GET /api/appointments/tickets/by_number/?number=TKT-001
```

##### 📊 Estadísticas de Tickets

- Método: GET
- URL: `http://localhost:8000/api/appointments/tickets/statistics/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

**¿Para qué sirve?**
- Obtiene **estadísticas generales** de todos los tickets
- Útil para dashboards y reportes ejecutivos
- **Ejemplo de uso**: "¿Cuál es el resumen de cobros del mes?"

**Respuesta 200 (ejemplo):**
```json
{
    "total_tickets": 25,
    "paid_tickets": 20,
    "pending_tickets": 3,
    "cancelled_tickets": 2,
    "paid_percentage": 80.0,
    "total_amount_paid": 3250.50
}
```

#### 📝 Campos del Modelo Ticket

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | Integer | Auto | ID único del ticket |
| `ticket_number` | String | Sí | Número único del ticket |
| `appointment` | Integer | Sí | ID de la cita asociada |
| `amount` | Decimal | Sí | Monto del ticket |
| `payment_method` | String | Sí | Método de pago (cash, card, transfer) |
| `payment_date` | DateTime | No | Fecha de pago |
| `status` | String | Sí | Estado del ticket (pending, paid, cancelled) |
| `description` | String | No | Descripción del ticket |
| `is_active` | Boolean | Sí | Indica si el ticket está activo |
| `reflexo_id` | Integer | Auto | ID de la empresa (tenant) |
| `created_at` | DateTime | Auto | Fecha de creación |
| `updated_at` | DateTime | Auto | Fecha de última actualización |

#### 🚨 Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| `400` | Datos inválidos | Revisar formato JSON y campos requeridos |
| `400` | Parámetros faltantes | Verificar parámetros requeridos en endpoints específicos |
| `401` | No autenticado | Verificar token JWT válido |
| `404` | Ticket no encontrado | Verificar que el ID del ticket existe |
| `409` | Conflicto | El número de ticket ya existe |
| `500` | Error del servidor | Revisar logs del servidor |

#### ⚠️ **Errores Comunes de Parámetros**

**Error en `by_ticket_number`:**
```json
{
    "error": "Se requiere ticket_number"
}
```
**Solución:** Usar `?ticket_number=TKT-001` en lugar de `?number=TKT-001`

**Error en `by_payment_method`:**
```json
{
    "error": "Se requiere payment_method (o alias: method)"
}
```
**Solución:** Usar `?payment_method=cash` o `?method=cash`

**Error en `by_number`:**
```json
{
    "error": "Se requiere number (o alias: ticket_number)"
}
```
**Solución:** Usar `?number=TKT-001` o `?ticket_number=TKT-001`

#### 📋 Validaciones

**Campos requeridos:**
- `ticket_number`: Número único del ticket
- `appointment`: ID de la cita (debe existir y estar activa)
- `amount`: Monto (debe ser mayor a 0)
- `payment_method`: Método de pago válido
- `status`: Estado válido del ticket

**Reglas de negocio:**
- Los tickets son multitenant (filtrados por `reflexo_id`)
- Unicidad por `ticket_number` dentro del tenant
- El ticket debe estar asociado a una cita válida
- Los tickets se crean automáticamente al crear una cita
- Hard delete por defecto (eliminación definitiva)
- Estados válidos: `pending`, `paid`, `cancelled`
- Métodos de pago válidos: `cash`, `card`, `transfer`

---

## 🧩 Módulo 6: Histories & Configurations (/api/configurations/)

> ⚠️ **IMPORTANTE - Seguridad por Tenant:**
> - **Recursos por Tenant:** Historiales Médicos, Precios Predeterminados
> - **Recursos Globales:** Tipos de Documento, Tipos de Pago, Estados de Pago
> - **Filtrado Automático:** Los usuarios solo ven datos de su empresa (`reflexo_id`)
> - **Administradores Globales:** Pueden ver todos los datos (requieren `is_superuser=True` o permiso `architect.view_all_tenants`)

### 📋 Historiales Médicos (/api/configurations/histories/)

#### 🔗 Endpoints

| Método | Endpoint                                    | Descripción                               | Autenticación |
|-------:|---------------------------------------------|-------------------------------------------|---------------|
|    GET | `/api/configurations/histories/`           | Listar historiales médicos                | Requerida     |
|   POST | `/api/configurations/histories/create/`    | Crear historial médico                    | Requerida     |
|    GET | `/api/configurations/histories/<int:pk>/` | Ver historial médico específico           | Requerida     |
|    PUT | `/api/configurations/histories/<int:pk>/edit/` | Editar historial (completo)         | Requerida     |
|  PATCH | `/api/configurations/histories/<int:pk>/edit/` | Editar historial (parcial)          | Requerida     |
| DELETE | `/api/configurations/histories/<int:pk>/delete/` | Eliminar historial médico         | Requerida     |

> ℹ️ Notas:
> - Los historiales son multitenant (filtrados por `reflexo_id`).
> - Usuario con tenant: solo ve historiales de su empresa.
> - Administrador global: puede ver todos los historiales.
> - Solo puede existir un historial activo por paciente.
> - Soft delete por defecto, hard delete con `?hard=true`.

#### 🧪 Ejemplos de Historiales Médicos

##### 📋 Listar Historiales Médicos

- Método: GET
- URL: `http://localhost:8000/api/configurations/histories/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "histories": [
        {
            "id": 1,
            "local_id": 1,
            "patient": 1,
            "patient_name": "Juan Pérez",
            "reflexo_id": 1
        },
        {
            "id": 2,
            "local_id": 2,
            "patient": 2,
            "patient_name": "María González",
            "reflexo_id": 1
        }
    ]
}
```

##### ➕ Crear Historial Médico

- Método: POST
- URL: `http://localhost:8000/api/configurations/histories/create/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

```json
{
    "patient": 1
}
```

- Respuesta 201 (ejemplo):

```json
{
    "id": 3,
    "reflexo_id": 1
}
```

- Respuesta 409 Conflict (historial ya existe):

```json
{
    "error": "Ya existe un historial activo para este paciente",
    "existing_history_id": 1
}
```

##### 👁️ Ver Historial Médico Específico

- Método: GET
- URL: `http://localhost:8000/api/configurations/histories/1/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "id": 1,
    "local_id": 1,
    "patient": 1,
    "patient_name": "Juan Pérez",
    "reflexo_id": 1,
    "testimony": true,
    "private_observation": "Observación interna del especialista",
    "observation": "Paciente refiere dolor lumbar leve",
    "height": 1.68,
    "weight": 62.5,
    "last_weight": 61.0,
    "menstruation": true,
    "diu_type": "Cobre",
    "gestation": false,
    "created_at": "2025-09-25T10:30:00Z",
    "updated_at": "2025-09-25T10:30:00Z"
}
```

##### ✏️ Editar Historial Médico (PUT completo)

- Método: PUT
- URL: `http://localhost:8000/api/configurations/histories/1/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición se aplica al historial identificado por el `id` en la URL.

```json
{
    "testimony": true,
    "private_observation": "Observación interna del especialista",
    "observation": "Paciente refiere dolor lumbar leve",
    "height": 1.68,
    "weight": 62.5,
    "last_weight": 61.0,
    "menstruation": true,
    "diu_type": "Cobre",
    "gestation": false
}
```

##### 🩹 Editar Historial Médico (PATCH parcial)

- Método: PATCH
- URL: `http://localhost:8000/api/configurations/histories/1/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición parcial se aplica al historial identificado por el `id` en la URL.

```json
{
    "private_observation": "Revisión posterior sin novedades",
    "observation": "Control a los 7 días"
}
```

##### 🗑️ Eliminar Historial Médico

- Método: DELETE
- URL: `http://localhost:8000/api/configurations/histories/1/delete/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

> ℹ️ Nota: La eliminación se aplica al historial identificado por el `id` en la URL.

- Respuesta 204 No Content (eliminación exitosa)

> **Nota sobre eliminación:** Por defecto realiza soft delete (marca `deleted_at`). Para eliminar definitivamente (hard delete), agrega `?hard=true` a la URL.

#### 📝 Campos del Modelo Historial Médico

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | Integer | Auto | ID único del historial |
| `local_id` | Integer | Auto | ID local por empresa |
| `patient` | Integer | Sí | ID del paciente |
| `testimony` | Boolean | No | Testimonio (default: true) |
| `private_observation` | String | No | Observación privada |
| `observation` | String | No | Observación general |
| `height` | Decimal | No | Altura en metros |
| `weight` | Decimal | No | Peso actual |
| `last_weight` | Decimal | No | Último peso registrado |
| `menstruation` | Boolean | No | Estado de menstruación (default: true) |
| `diu_type` | String | No | Tipo de DIU |
| `gestation` | Boolean | No | Estado de gestación (default: true) |
| `reflexo_id` | Integer | Auto | ID de la empresa (tenant) |
| `created_at` | DateTime | Auto | Fecha de creación |
| `updated_at` | DateTime | Auto | Fecha de última actualización |
| `deleted_at` | DateTime | Auto | Fecha de eliminación (soft delete) |

#### 🚨 Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| `400` | Datos inválidos | Revisar formato JSON y campos requeridos |
| `401` | No autenticado | Verificar token JWT válido |
| `403` | No autorizado | El paciente no pertenece a tu empresa |
| `404` | Historial no encontrado | Verificar que el ID del historial existe |
| `409` | Conflicto | Ya existe un historial activo para este paciente |
| `500` | Error del servidor | Revisar logs del servidor |

#### 📋 Validaciones

**Campos requeridos:**
- `patient`: ID del paciente (debe existir y estar activo)

**Reglas de negocio:**
- Los historiales son multitenant (filtrados por `reflexo_id`)
- Solo puede existir un historial activo por paciente
- El paciente debe pertenecer al mismo tenant del usuario
- Soft delete por defecto (marca `deleted_at`)
- Hard delete disponible con `?hard=true`
- Validación de unicidad por paciente activo

---

### 📄 Tipos de Documento (/api/configurations/document_types/)

#### 🔗 Endpoints

| Método | Endpoint                                          | Descripción                               | Autenticación |
|-------:|---------------------------------------------------|-------------------------------------------|---------------|
|    GET | `/api/configurations/document_types/`            | Listar tipos de documento                 | No requerida  |
|   POST | `/api/configurations/document_types/create/`     | Crear tipo de documento                   | No requerida  |
|    GET | `/api/configurations/document_types/<int:pk>/`  | Ver tipo de documento específico          | No requerida  |
|    PUT | `/api/configurations/document_types/<int:pk>/edit/` | Editar tipo (completo)              | No requerida  |
|  PATCH | `/api/configurations/document_types/<int:pk>/edit/` | Editar tipo (parcial)               | No requerida  |
| DELETE | `/api/configurations/document_types/<int:pk>/delete/` | Eliminar tipo de documento      | No requerida  |

> ℹ️ Notas:
> - Los tipos de documento son **GLOBALES** (no multitenant).
> - Todos los usuarios pueden ver todos los tipos.
> - Hard delete por defecto (eliminación definitiva).

#### 🧪 Ejemplos de Tipos de Documento

##### 📋 Listar Tipos de Documento

- Método: GET
- URL: `http://localhost:8000/api/configurations/document_types/`
- Headers:
  - `Content-Type: application/json`

- Respuesta 200 (ejemplo):

```json
{
    "document_types": [
        {
            "id": 1,
            "name": "DNI"
        },
        {
            "id": 2,
            "name": "Carné de Extranjería"
        },
        {
            "id": 3,
            "name": "Pasaporte"
        }
    ]
}
```

##### ➕ Crear Tipo de Documento

- Método: POST
- URL: `http://localhost:8000/api/configurations/document_types/create/`
- Headers:
  - `Content-Type: application/json`
- Body → raw → JSON

```json
{
    "name": "Factura"
}
```

- Respuesta 201 (ejemplo):

```json
{
    "id": 4,
    "name": "Factura"
}
```

##### 👁️ Ver Tipo de Documento Específico

- Método: GET
- URL: `http://localhost:8000/api/configurations/document_types/1/`
- Headers:
  - `Content-Type: application/json`

- Respuesta 200 (ejemplo):

```json
{
    "id": 1,
    "name": "DNI",
    "created_at": "2025-09-25T10:30:00Z",
    "updated_at": "2025-09-25T10:30:00Z"
}
```

##### ✏️ Editar Tipo de Documento (PUT completo)

- Método: PUT
- URL: `http://localhost:8000/api/configurations/document_types/1/edit/`
- Headers:
  - `Content-Type: application/json`
- Body → raw → JSON

> ℹ️ Nota: La edición se aplica al tipo identificado por el `id` en la URL.

```json
{
    "name": "Documento Nacional de Identidad"
}
```

##### 🩹 Editar Tipo de Documento (PATCH parcial)

- Método: PATCH
- URL: `http://localhost:8000/api/configurations/document_types/1/edit/`
- Headers:
  - `Content-Type: application/json`
- Body → raw → JSON

> ℹ️ Nota: La edición parcial se aplica al tipo identificado por el `id` en la URL.

```json
{
    "name": "DNI Actualizado"
}
```

##### 🗑️ Eliminar Tipo de Documento

- Método: DELETE
- URL: `http://localhost:8000/api/configurations/document_types/1/delete/`
- Headers:
  - `Content-Type: application/json`

> ℹ️ Nota: La eliminación se aplica al tipo identificado por el `id` en la URL.

- Respuesta 204 No Content (eliminación exitosa)

> **Nota sobre eliminación:** Realiza eliminación DEFINITIVA (hard delete) GLOBAL. El registro se elimina de la base de datos y no aparece en la API ni en Django Admin.

#### 📝 Campos del Modelo Tipo de Documento

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | Integer | Auto | ID único del tipo |
| `name` | String | Sí | Nombre del tipo de documento |
| `created_at` | DateTime | Auto | Fecha de creación |
| `updated_at` | DateTime | Auto | Fecha de última actualización |
| `deleted_at` | DateTime | Auto | Fecha de eliminación (soft delete) |

#### 🚨 Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| `400` | Datos inválidos | Revisar formato JSON y campos requeridos |
| `404` | Tipo no encontrado | Verificar que el ID del tipo existe |
| `500` | Error del servidor | Revisar logs del servidor |

#### 📋 Validaciones

**Campos requeridos:**
- `name`: Nombre del tipo de documento

**Reglas de negocio:**
- Los tipos son globales (no multitenant)
- Hard delete por defecto (eliminación definitiva)
- No hay restricciones de unicidad global

---

### 💳 Tipos de Pago (/api/configurations/payment_types/)

#### 🔗 Endpoints

| Método | Endpoint                                          | Descripción                               | Autenticación |
|-------:|---------------------------------------------------|-------------------------------------------|---------------|
|    GET | `/api/configurations/payment_types/`             | Listar tipos de pago                      | No requerida  |
|   POST | `/api/configurations/payment_types/create/`      | Crear tipo de pago                        | No requerida  |
|    GET | `/api/configurations/payment_types/<int:pk>/`   | Ver tipo de pago específico               | No requerida  |
|    PUT | `/api/configurations/payment_types/<int:pk>/edit/` | Editar tipo (completo)              | No requerida  |
|  PATCH | `/api/configurations/payment_types/<int:pk>/edit/` | Editar tipo (parcial)               | No requerida  |
| DELETE | `/api/configurations/payment_types/<int:pk>/delete/` | Eliminar tipo de pago            | No requerida  |

> ℹ️ Notas:
> - Los tipos de pago son **GLOBALES** (no multitenant).
> - Todos los usuarios pueden ver todos los tipos.
> - Hard delete por defecto (eliminación definitiva).

#### 🧪 Ejemplos de Tipos de Pago

##### 📋 Listar Tipos de Pago

- Método: GET
- URL: `http://localhost:8000/api/configurations/payment_types/`
- Headers:
  - `Content-Type: application/json`

- Respuesta 200 (ejemplo):

```json
{
    "payment_types": [
        {
            "id": 1,
            "name": "Efectivo"
        },
        {
            "id": 2,
            "name": "Tarjeta de Crédito"
        },
        {
            "id": 3,
            "name": "Transferencia Bancaria"
        }
    ]
}
```

##### ➕ Crear Tipo de Pago

- Método: POST
- URL: `http://localhost:8000/api/configurations/payment_types/create/`
- Headers:
  - `Content-Type: application/json`
- Body → raw → JSON

```json
{
    "name": "Yape"
}
```

- Respuesta 201 (ejemplo):

```json
{
    "id": 4,
    "name": "Yape"
}
```

##### 👁️ Ver Tipo de Pago Específico

- Método: GET
- URL: `http://localhost:8000/api/configurations/payment_types/1/`
- Headers:
  - `Content-Type: application/json`

- Respuesta 200 (ejemplo):

```json
{
    "id": 1,
    "name": "Efectivo",
    "created_at": "2025-09-25T10:30:00Z",
    "updated_at": "2025-09-25T10:30:00Z"
}
```

##### ✏️ Editar Tipo de Pago (PUT completo)

- Método: PUT
- URL: `http://localhost:8000/api/configurations/payment_types/1/edit/`
- Headers:
  - `Content-Type: application/json`
- Body → raw → JSON

> ℹ️ Nota: La edición se aplica al tipo identificado por el `id` en la URL.

```json
{
    "name": "Pago en Efectivo"
}
```

##### 🩹 Editar Tipo de Pago (PATCH parcial)

- Método: PATCH
- URL: `http://localhost:8000/api/configurations/payment_types/1/edit/`
- Headers:
  - `Content-Type: application/json`
- Body → raw → JSON

> ℹ️ Nota: La edición parcial se aplica al tipo identificado por el `id` en la URL.

```json
{
    "name": "Efectivo Actualizado"
}
```

##### 🗑️ Eliminar Tipo de Pago

- Método: DELETE
- URL: `http://localhost:8000/api/configurations/payment_types/1/delete/`
- Headers:
  - `Content-Type: application/json`

> ℹ️ Nota: La eliminación se aplica al tipo identificado por el `id` en la URL.

- Respuesta 204 No Content (eliminación exitosa)

> **Nota sobre eliminación:** Realiza eliminación DEFINITIVA (hard delete) GLOBAL. El registro se elimina de la base de datos y no aparece en la API ni en Django Admin.

#### 📝 Campos del Modelo Tipo de Pago

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | Integer | Auto | ID único del tipo |
| `name` | String | Sí | Nombre del tipo de pago |
| `created_at` | DateTime | Auto | Fecha de creación |
| `updated_at` | DateTime | Auto | Fecha de última actualización |
| `deleted_at` | DateTime | Auto | Fecha de eliminación (soft delete) |

#### 🚨 Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| `400` | Datos inválidos | Revisar formato JSON y campos requeridos |
| `404` | Tipo no encontrado | Verificar que el ID del tipo existe |
| `500` | Error del servidor | Revisar logs del servidor |

#### 📋 Validaciones

**Campos requeridos:**
- `name`: Nombre del tipo de pago

**Reglas de negocio:**
- Los tipos son globales (no multitenant)
- Hard delete por defecto (eliminación definitiva)
- No hay restricciones de unicidad global

---

### 📊 Estados de Pago (/api/configurations/payment_statuses/)

#### 🔗 Endpoints

| Método | Endpoint                                          | Descripción                               | Autenticación |
|-------:|---------------------------------------------------|-------------------------------------------|---------------|
|    GET | `/api/configurations/payment_statuses/`          | Listar estados de pago                    | No requerida  |
|   POST | `/api/configurations/payment_statuses/create/`   | Crear estado de pago                      | No requerida  |
|    GET | `/api/configurations/payment_statuses/<int:pk>/` | Ver estado de pago específico             | No requerida  |
|    PUT | `/api/configurations/payment_statuses/<int:pk>/edit/` | Editar estado (completo)          | No requerida  |
|  PATCH | `/api/configurations/payment_statuses/<int:pk>/edit/` | Editar estado (parcial)           | No requerida  |
| DELETE | `/api/configurations/payment_statuses/<int:pk>/delete/` | Eliminar estado de pago         | No requerida  |

> ℹ️ Notas:
> - Los estados de pago son **GLOBALES** (no multitenant).
> - Todos los usuarios pueden ver todos los estados.
> - Hard delete por defecto (eliminación definitiva).
> - **Campos del modelo:** `id`, `name`, `description` (sin campos de auditoría).

#### 🧪 Ejemplos de Estados de Pago

##### 📋 Listar Estados de Pago

- Método: GET
- URL: `http://localhost:8000/api/configurations/payment_statuses/`
- Headers:
  - `Content-Type: application/json`

- Respuesta 200 (ejemplo):

```json
{
    "payment_statuses": [
        {
            "id": 1,
            "name": "Pendiente",
            "description": "Pago pendiente de confirmación"
        },
        {
            "id": 2,
            "name": "Pagado",
            "description": "Pago confirmado y procesado"
        },
        {
            "id": 3,
            "name": "Cancelado",
            "description": "Pago cancelado o rechazado"
        }
    ]
}
```

##### ➕ Crear Estado de Pago

- Método: POST
- URL: `http://localhost:8000/api/configurations/payment_statuses/create/`
- Headers:
  - `Content-Type: application/json`
- Body → raw → JSON

```json
{
    "name": "Reembolsado",
    "description": "Pago reembolsado al cliente"
}
```

- Respuesta 201 (ejemplo):

```json
{
    "id": 4,
    "name": "Reembolsado",
    "description": "Pago reembolsado al cliente"
}
```

##### 👁️ Ver Estado de Pago Específico

- Método: GET
- URL: `http://localhost:8000/api/configurations/payment_statuses/1/`
- Headers:
  - `Content-Type: application/json`

- Respuesta 200 (ejemplo):

```json
{
    "id": 1,
    "name": "Pendiente",
    "description": "Pago pendiente de confirmación"
}
```

##### ✏️ Editar Estado de Pago (PUT completo)

- Método: PUT
- URL: `http://localhost:8000/api/configurations/payment_statuses/1/edit/`
- Headers:
  - `Content-Type: application/json`
- Body → raw → JSON

> ℹ️ Nota: La edición se aplica al estado identificado por el `id` en la URL.

```json
{
    "name": "Pendiente",
    "description": "Pago pendiente de confirmación y validación"
}
```

##### 🩹 Editar Estado de Pago (PATCH parcial)

- Método: PATCH
- URL: `http://localhost:8000/api/configurations/payment_statuses/1/edit/`
- Headers:
  - `Content-Type: application/json`
- Body → raw → JSON

> ℹ️ Nota: La edición parcial se aplica al estado identificado por el `id` en la URL.

```json
{
    "description": "Pago pendiente de confirmación actualizado"
}
```

##### 🗑️ Eliminar Estado de Pago

- Método: DELETE
- URL: `http://localhost:8000/api/configurations/payment_statuses/1/delete/`
- Headers:
  - `Content-Type: application/json`

> ℹ️ Nota: La eliminación se aplica al estado identificado por el `id` en la URL.

- Respuesta 204 No Content (eliminación exitosa)

> **Nota sobre eliminación:** Realiza eliminación DEFINITIVA (hard delete) GLOBAL. El registro se elimina de la base de datos y no aparece en la API ni en Django Admin.

#### 📝 Campos del Modelo Estado de Pago

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | Integer | Auto | ID único del estado |
| `name` | String | Sí | Nombre del estado de pago |
| `description` | String | No | Descripción del estado |

#### 🚨 Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| `400` | Datos inválidos | Revisar formato JSON y campos requeridos |
| `404` | Estado no encontrado | Verificar que el ID del estado existe |
| `500` | Error del servidor | Revisar logs del servidor |

#### 📋 Validaciones

**Campos requeridos:**
- `name`: Nombre del estado de pago

**Reglas de negocio:**
- Los estados son globales (no multitenant)
- Hard delete por defecto (eliminación definitiva)
- No hay restricciones de unicidad global

---

### 💰 Precios Predeterminados (/api/configurations/predetermined_prices/)

#### 🔗 Endpoints

| Método | Endpoint                                          | Descripción                               | Autenticación |
|-------:|---------------------------------------------------|-------------------------------------------|---------------|
|    GET | `/api/configurations/predetermined_prices/`      | Listar precios predeterminados            | Requerida     |
|   POST | `/api/configurations/predetermined_prices/create/` | Crear precio predeterminado            | Requerida     |
|    GET | `/api/configurations/predetermined_prices/<int:pk>/` | Ver precio específico              | Requerida     |
|    PUT | `/api/configurations/predetermined_prices/<int:pk>/edit/` | Editar precio (completo)        | Requerida     |
|  PATCH | `/api/configurations/predetermined_prices/<int:pk>/edit/` | Editar precio (parcial)         | Requerida     |
| DELETE | `/api/configurations/predetermined_prices/<int:pk>/delete/` | Eliminar precio predeterminado | Requerida     |

> ℹ️ Notas:
> - Los precios predeterminados son multitenant (filtrados por `reflexo_id`).
> - Usuario con tenant: solo ve precios de su empresa.
> - Administrador global: puede ver todos los precios.
> - Hard delete por defecto (eliminación definitiva).

#### 🧪 Ejemplos de Precios Predeterminados

##### 📋 Listar Precios Predeterminados

- Método: GET
- URL: `http://localhost:8000/api/configurations/predetermined_prices/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "predetermined_prices": [
        {
            "id": 1,
            "name": "Consulta General",
            "price": "150.00"
        },
        {
            "id": 2,
            "name": "Consulta Especializada",
            "price": "200.00"
        },
        {
            "id": 3,
            "name": "Terapia Física",
            "price": "120.00"
        }
    ]
}
```

##### ➕ Crear Precio Predeterminado

- Método: POST
- URL: `http://localhost:8000/api/configurations/predetermined_prices/create/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

```json
{
    "name": "Consulta de Emergencia",
    "price": 300.00
}
```

- Respuesta 201 (ejemplo):

```json
{
    "id": 4,
    "reflexo_id": 1
}
```

##### 👁️ Ver Precio Predeterminado Específico

- Método: GET
- URL: `http://localhost:8000/api/configurations/predetermined_prices/1/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "id": 1,
    "name": "Consulta General",
    "price": "150.00",
    "reflexo_id": 1,
    "created_at": "2025-09-25T10:30:00Z",
    "updated_at": "2025-09-25T10:30:00Z"
}
```

##### ✏️ Editar Precio Predeterminado (PUT completo)

- Método: PUT
- URL: `http://localhost:8000/api/configurations/predetermined_prices/1/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición se aplica al precio identificado por el `id` en la URL.

```json
{
    "name": "Consulta General",
    "price": 180.00
}
```

##### 🩹 Editar Precio Predeterminado (PATCH parcial)

- Método: PATCH
- URL: `http://localhost:8000/api/configurations/predetermined_prices/1/edit/`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <jwt_access_token>`
- Body → raw → JSON

> ℹ️ Nota: La edición parcial se aplica al precio identificado por el `id` en la URL.

```json
{
    "price": 200.00
}
```

##### 🗑️ Eliminar Precio Predeterminado

- Método: DELETE
- URL: `http://localhost:8000/api/configurations/predetermined_prices/1/delete/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

> ℹ️ Nota: La eliminación se aplica al precio identificado por el `id` en la URL.

- Respuesta 204 No Content (eliminación exitosa)

> **Nota sobre eliminación:** Realiza eliminación DEFINITIVA (hard delete). El registro se elimina de la base de datos y no aparece en la API ni en Django Admin.

#### 📝 Campos del Modelo Precio Predeterminado

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | Integer | Auto | ID único del precio |
| `name` | String | Sí | Nombre del servicio/precio |
| `price` | Decimal | Sí | Precio del servicio |
| `reflexo_id` | Integer | Auto | ID de la empresa (tenant) |
| `created_at` | DateTime | Auto | Fecha de creación |
| `updated_at` | DateTime | Auto | Fecha de última actualización |
| `deleted_at` | DateTime | Auto | Fecha de eliminación (soft delete) |

#### 🚨 Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| `400` | Datos inválidos | Revisar formato JSON y campos requeridos |
| `401` | No autenticado | Verificar token JWT válido |
| `403` | No autorizado | Usuario sin empresa asignada |
| `404` | Precio no encontrado | Verificar que el ID del precio existe |
| `500` | Error del servidor | Revisar logs del servidor |

#### 📋 Validaciones

**Campos requeridos:**
- `name`: Nombre del servicio/precio
- `price`: Precio del servicio (debe ser mayor a 0)

**Reglas de negocio:**
- Los precios son multitenant (filtrados por `reflexo_id`)
- Usuario con tenant: solo puede ver/editar precios de su empresa
- Administrador global: debe especificar `reflexo_id` al crear
- Hard delete por defecto (eliminación definitiva)
- Validación de tenant para usuarios no-admin

---

## 🧩 Módulo 7: Locations (/api/locations/)

> ⚠️ **IMPORTANTE - Recursos Globales:**
> - **Recursos Globales:** Regiones, Provincias, Distritos son datos de referencia globales
> - **Solo Lectura:** Todos los endpoints son GET (solo consulta)
> - **Jerarquía Geográfica:** Región → Provincia → Distrito
> - **Filtros Disponibles:** Por región (`?region=<id>`) y provincia (`?province=<id>`)

### 🏞️ Regiones (/api/locations/regions/)

#### 🔗 Endpoints

| Método | Endpoint                                    | Descripción                               | Autenticación |
|-------:|---------------------------------------------|-------------------------------------------|---------------|
|    GET | `/api/locations/regions/`                  | Listar regiones                           | Requerida     |
|    GET | `/api/locations/regions/<int:pk>/`        | Ver región específica                     | Requerida     |

> ℹ️ Notas:
> - Las regiones son recursos globales (no multitenant).
> - Todos los usuarios autenticados ven las mismas regiones.
> - Solo lectura (endpoints GET únicamente).
> - Usar el campo `id` de cada región como `region_id` en la creación de pacientes.

#### 🧪 Ejemplos de Regiones

##### 📋 Listar Regiones

- Método: GET
- URL: `http://localhost:8000/api/locations/regions/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
[
    {
        "id": 1,
        "name": "Lima",
        "ubigeo_code": 15,
        "created_at": "2025-09-25T10:30:00Z",
        "updated_at": "2025-09-25T10:30:00Z",
        "deleted_at": null
    },
    {
        "id": 2,
        "name": "Arequipa",
        "ubigeo_code": 4,
        "created_at": "2025-09-25T10:30:00Z",
        "updated_at": "2025-09-25T10:30:00Z",
        "deleted_at": null
    }
]
```

##### 👁️ Ver Región Específica

- Método: GET
- URL: `http://localhost:8000/api/locations/regions/1/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "id": 1,
    "name": "Lima",
    "ubigeo_code": 15,
    "created_at": "2025-09-25T10:30:00Z",
    "updated_at": "2025-09-25T10:30:00Z",
    "deleted_at": null
}
```

#### 📝 Campos del Modelo Región

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | ID único de la región |
| `name` | String | Nombre de la región |
| `ubigeo_code` | Integer | Código ubigeo de la región |
| `created_at` | DateTime | Fecha de creación |
| `updated_at` | DateTime | Fecha de última actualización |
| `deleted_at` | DateTime | Fecha de eliminación (soft delete) |

#### 🚨 Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| `401` | No autenticado | Verificar token JWT válido |
| `404` | Región no encontrada | Verificar que el ID de la región existe |
| `500` | Error del servidor | Revisar logs del servidor |

#### 📋 Notas Importantes

- **Recursos globales:** Las regiones son datos de referencia compartidos
- **Solo lectura:** No se pueden crear, editar o eliminar regiones via API
- **Uso en pacientes:** Usar el campo `id` de la región como `region_id` al crear pacientes

---

### 🏙️ Provincias (/api/locations/provinces/)

#### 🔗 Endpoints

| Método | Endpoint                                      | Descripción                               | Autenticación |
|-------:|-----------------------------------------------|-------------------------------------------|---------------|
|    GET | `/api/locations/provinces/`                  | Listar provincias                         | Requerida     |
|    GET | `/api/locations/provinces/<int:pk>/`        | Ver provincia específica                  | Requerida     |

> ℹ️ Notas:
> - Las provincias son recursos globales (no multitenant).
> - Todos los usuarios autenticados ven las mismas provincias.
> - Solo lectura (endpoints GET únicamente).
> - Filtro por región: `?region=<region_id>` (ejemplo: `?region=1`)
> - Usar el campo `id` de cada provincia como `province_id` en la creación de pacientes.

#### 🧪 Ejemplos de Provincias

##### 📋 Listar Provincias

- Método: GET
- URL: `http://localhost:8000/api/locations/provinces/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
[
    {
        "id": 1,
        "name": "Lima",
        "ubigeo_code": 1501,
        "sequence": 1,
        "region": 1,
        "region_name": "Lima",
        "created_at": "2025-09-25T10:30:00Z",
        "updated_at": "2025-09-25T10:30:00Z",
        "deleted_at": null
    },
    {
        "id": 2,
        "name": "Callao",
        "ubigeo_code": 1502,
        "sequence": 2,
        "region": 1,
        "region_name": "Lima",
        "created_at": "2025-09-25T10:30:00Z",
        "updated_at": "2025-09-25T10:30:00Z",
        "deleted_at": null
    }
]
```

##### 📋 Listar Provincias por Región

- Método: GET
- URL: `http://localhost:8000/api/locations/provinces/?region=1`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
[
    {
        "id": 1,
        "name": "Lima",
        "ubigeo_code": 1501,
        "sequence": 1,
        "region": 1,
        "region_name": "Lima",
        "created_at": "2025-09-25T10:30:00Z",
        "updated_at": "2025-09-25T10:30:00Z",
        "deleted_at": null
    }
]
```

##### 👁️ Ver Provincia Específica

- Método: GET
- URL: `http://localhost:8000/api/locations/provinces/1/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "id": 1,
    "name": "Lima",
    "ubigeo_code": 1501,
    "sequence": 1,
    "region": 1,
    "region_name": "Lima",
    "created_at": "2025-09-25T10:30:00Z",
    "updated_at": "2025-09-25T10:30:00Z",
    "deleted_at": null
}
```

#### 📝 Campos del Modelo Provincia

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | ID único de la provincia |
| `name` | String | Nombre de la provincia |
| `ubigeo_code` | Integer | Código ubigeo de la provincia |
| `sequence` | Integer | Número de secuencia visual |
| `region` | Integer | ID de la región |
| `region_name` | String | Nombre de la región (read-only) |
| `created_at` | DateTime | Fecha de creación |
| `updated_at` | DateTime | Fecha de última actualización |
| `deleted_at` | DateTime | Fecha de eliminación (soft delete) |

#### 🚨 Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| `401` | No autenticado | Verificar token JWT válido |
| `404` | Provincia no encontrada | Verificar que el ID de la provincia existe |
| `500` | Error del servidor | Revisar logs del servidor |

#### 📋 Notas Importantes

- **Recursos globales:** Las provincias son datos de referencia compartidos
- **Solo lectura:** No se pueden crear, editar o eliminar provincias via API
- **Filtro por región:** Usar `?region=<region_id>` para filtrar por región
- **Uso en pacientes:** Usar el campo `id` de la provincia como `province_id` al crear pacientes

---

### 🏘️ Distritos (/api/locations/districts/)

#### 🔗 Endpoints

| Método | Endpoint                                      | Descripción                               | Autenticación |
|-------:|-----------------------------------------------|-------------------------------------------|---------------|
|    GET | `/api/locations/districts/`                  | Listar distritos                          | Requerida     |
|    GET | `/api/locations/districts/<int:pk>/`        | Ver distrito específico                   | Requerida     |

> ℹ️ Notas:
> - Los distritos son recursos globales (no multitenant).
> - Todos los usuarios autenticados ven los mismos distritos.
> - Solo lectura (endpoints GET únicamente).
> - Filtro por provincia: `?province=<province_id>` (ejemplo: `?province=1`)
> - Usar el campo `id` de cada distrito como `district_id` en la creación de pacientes.

#### 🧪 Ejemplos de Distritos

##### 📋 Listar Distritos

- Método: GET
- URL: `http://localhost:8000/api/locations/districts/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
[
    {
        "id": 1,
        "name": "Miraflores",
        "ubigeo_code": 150101,
        "sequence": 1,
        "province": 1,
        "province_name": "Lima",
        "region_name": "Lima",
        "created_at": "2025-09-25T10:30:00Z",
        "updated_at": "2025-09-25T10:30:00Z",
        "deleted_at": null
    },
    {
        "id": 2,
        "name": "San Isidro",
        "ubigeo_code": 150102,
        "sequence": 2,
        "province": 1,
        "province_name": "Lima",
        "region_name": "Lima",
        "created_at": "2025-09-25T10:30:00Z",
        "updated_at": "2025-09-25T10:30:00Z",
        "deleted_at": null
    }
]
```

##### 📋 Listar Distritos por Provincia

- Método: GET
- URL: `http://localhost:8000/api/locations/districts/?province=1`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
[
    {
        "id": 1,
        "name": "Miraflores",
        "ubigeo_code": 150101,
        "sequence": 1,
        "province": 1,
        "province_name": "Lima",
        "region_name": "Lima",
        "created_at": "2025-09-25T10:30:00Z",
        "updated_at": "2025-09-25T10:30:00Z",
        "deleted_at": null
    }
]
```

##### 👁️ Ver Distrito Específico

- Método: GET
- URL: `http://localhost:8000/api/locations/districts/1/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "id": 1,
    "name": "Miraflores",
    "ubigeo_code": 150101,
    "sequence": 1,
    "province": 1,
    "province_name": "Lima",
    "region_name": "Lima",
    "created_at": "2025-09-25T10:30:00Z",
    "updated_at": "2025-09-25T10:30:00Z",
    "deleted_at": null
}
```

#### 📝 Campos del Modelo Distrito

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | ID único del distrito |
| `name` | String | Nombre del distrito |
| `ubigeo_code` | Integer | Código ubigeo del distrito |
| `sequence` | Integer | Número de secuencia visual |
| `province` | Integer | ID de la provincia |
| `province_name` | String | Nombre de la provincia (read-only) |
| `region_name` | String | Nombre de la región (read-only) |
| `created_at` | DateTime | Fecha de creación |
| `updated_at` | DateTime | Fecha de última actualización |
| `deleted_at` | DateTime | Fecha de eliminación (soft delete) |

#### 🚨 Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| `401` | No autenticado | Verificar token JWT válido |
| `404` | Distrito no encontrado | Verificar que el ID del distrito existe |
| `500` | Error del servidor | Revisar logs del servidor |

#### 📋 Notas Importantes

- **Recursos globales:** Los distritos son datos de referencia compartidos
- **Solo lectura:** No se pueden crear, editar o eliminar distritos via API
- **Filtro por provincia:** Usar `?province=<province_id>` para filtrar por provincia
- **Uso en pacientes:** Usar el campo `id` del distrito como `district_id` al crear pacientes

---

## 🧩 Módulo 8: Company Reports Module

### 🏢 Datos de Empresa (/api/company/company/)

#### 🔗 Endpoints

| Método | Endpoint | Descripción | Autenticación |
|-------:|----------|-------------|---------------|
|    GET | `/api/company/company/` | Listar empresas | Requerida |
|   POST | `/api/company/company/create/` | Crear empresa | Requerida |
|    GET | `/api/company/company/<int:pk>/show/` | Ver empresa específica | Requerida |
|    PUT | `/api/company/company/<int:pk>/edit/` | Actualizar empresa | Requerida |
| DELETE | `/api/company/company/<int:pk>/delete/` | Eliminar empresa | Requerida |
|   POST | `/api/company/company/<int:pk>/upload_logo/` | Subir logo | Requerida |
| DELETE | `/api/company/company/<int:pk>/delete_logo/` | Eliminar logo | Requerida |
|    GET | `/api/company/company/<int:pk>/show_logo/` | Mostrar logo | Requerida |

> ℹ️ Notas:
> - Los datos de empresa son multitenant (filtrados por `reflexo_id`).
> - Los administradores globales ven todas las empresas.
> - Usar `/store/` para crear empresas con asignación automática de tenant.
> - Los logos se almacenan en `company_logos/` con validación de extensiones.
> - Eliminación es hard delete (definitiva).

#### 🧪 Ejemplos de Datos de Empresa

##### 📋 Listar Empresas

- Método: GET
- URL: `http://localhost:8000/api/company/company/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "status": "success",
    "data": [
        {
            "id": 1,
            "reflexo": 1,
            "company_name": "Clínica San José",
            "company_logo": null,
            "logo_url": null,
            "has_logo": false,
            "created_at": "2025-09-25T10:30:00Z",
            "updated_at": "2025-09-25T10:30:00Z"
        }
    ]
}
```

##### ➕ Crear Empresa

- Método: POST
- URL: `http://localhost:8000/api/company/company/create/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`
  - `Content-Type: application/json`

- Body JSON:

```json
{
    "company_name": "Reflexo"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "id": 1,
    "company_name": "Reflexo",
    "company_logo": null,
    "logo_url": null,
    "has_logo": false,
    "created_at": "2025-08-24T04:15:38.320819Z",
    "updated_at": "2025-08-24T04:15:38.320839Z"
}
```

**Posibles Errores al crear el nombre de la empresa:**
```json
{
    "company_name": [
        "Company Data with this company name already exists."
    ]
}
```

**Nota Importante sobre crear la empresa:**
Al crear una empresa no se tiene que poner el mismo nombre, la idea es solo usar la única empresa creada y editarla aunque se pueda crear más.

##### 👁️ Ver Empresa Específica

- Método: GET
- URL: `http://localhost:8000/api/company/company/1/show/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "id": 1,
    "reflexo": 1,
    "company_name": "Clínica San José",
    "company_logo": null,
    "logo_url": null,
    "has_logo": false,
    "created_at": "2025-09-25T10:30:00Z",
    "updated_at": "2025-09-25T10:30:00Z"
}
```

##### ✏️ Actualizar Empresa

**SOLO ACTUALIZAR EL NOMBRE:**
- Método: PUT
- URL: `http://localhost:8000/api/company/company/1/edit/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`
  - `Content-Type: application/json`

- Body JSON:

```json
{
    "company_name": "empresaT"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "id": 1,
    "company_name": "empresaT",
    "company_logo": "empresaT.jpg",
    "logo_url": "http://127.0.0.1:8000/media/logos/oskar-smethurst-B1GtwanCbiw-unsplash_1.jpg",
    "has_logo": true,
    "created_at": "2025-08-24T16:24:25.239714Z",
    "updated_at": "2025-08-24T16:51:54.849350Z"
}
```

**ACTUALIZAR NOMBRE Y LOGO:**
- Método: PUT
- URL: `http://localhost:8000/api/company/company/1/edit/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Body Form-Data:
  | Key | Value |
  |-----|-------|
  | `company_name` [text] | reflexo |
  | `company_logo` [file] | *escoger imagen* |

- Respuesta 200 (ejemplo):

```json
{
    "id": 1,
    "company_name": "reflexo",
    "company_logo": "reflexo.jpg",
    "logo_url": "http://127.0.0.1:8000/media/logos/oskar-smethurst-B1GtwanCbiw-unsplash_1.jpg",
    "has_logo": true,
    "created_at": "2025-08-24T16:24:25.239714Z",
    "updated_at": "2025-08-24T17:01:41.761879Z"
}
```

**Advertencias:**
```json
{
    "warning": "El logo no se actualizó: Formato no permitido. Solo se aceptan: jpg, jpeg, png",
    "id": 1,
    "company_name": "reflexo",
    "company_logo": "reflexo.jpg",
    "logo_url": "http://127.0.0.1:8000/media/logos/oskar-smethurst-B1GtwanCbiw-unsplash_1.jpg",
    "has_logo": true,
    "created_at": "2025-08-24T16:24:25.239714Z",
    "updated_at": "2025-08-24T17:15:02.281286Z"
}
```

**Nota Importante Actualizar Empresa:**
- Hay dos maneras de actualizar una por "raw" solo actualiza el nombre y la otra manera "Form-data" permite ambos el nombre y el logo
- La imagen se actualiza solo si es un formato de imagen permitido o si no pasa los 2mb de lo contrario te da una advertencia y se queda la imagen que ya tenía antes
- Si pones PATCH en vez de PUT realiza lo mismo

##### 🖼️ Subir Logo

- Método: POST
- URL: `http://localhost:8000/api/company/company/1/upload_logo/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`
  - `Content-Type: application/json`

- Body JSON:

```json
{
    "company_logo": "https://ejemplo.com/logo.png"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "message": "Logo subido correctamente",
    "logo_url": "https://ejemplo.com/logo.png"
}
```

##### 🗑️ Eliminar Empresa

- Método: DELETE
- URL: `http://localhost:8000/api/company/company/1/delete/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "status": "success",
    "message": "Empresa \"Clínica San José\" eliminada correctamente"
}
```

##### 🖼️ Subir Logo

- Método: POST
- URL: `http://localhost:8000/api/company/company/1/upload_logo/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Body Form-Data:
  | Key | Value |
  |-----|-------|
  | `logo` [file] | *escoger imagen* |

- Respuesta 200 (ejemplo):

```json
{
    "message": "Logo subido correctamente"
}
```

**Posibles Errores al subir el logo:**

```json
{
    "logo": [
        "Solo se permiten imágenes JPG o PNG."
    ]
}
```

```json
{
    "logo": [
        "El logo no puede superar los 2 MB."
    ]
}
```

```json
{
    "error": "La empresa ya tiene un logo. Use PUT para actualizar."
}
```

**Nota Importante sobre subir logo:**
- Colocar en la parte de key "logo" y seleccionar file, por defecto está text
- No subir una imagen de más de 2mb
- Solo se puede subir un logo si la empresa no cuenta con ella, para actualizar se usa PUT

##### 🔄 Actualizar Logo (PUT)

- Método: PUT
- URL: `http://localhost:8000/api/company/company/1/upload_logo/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`
  - `Content-Type: application/json`

- Body JSON:

```json
{
    "company_logo": "https://nuevo-logo.com/logo-actualizado.png"
}
```

- Respuesta 200 (ejemplo):

```json
{
    "message": "Logo actualizado correctamente",
    "company_logo": "/media/company/empresa_logo_nuevo.png",
    "company_logo_absolute": "http://localhost:8000/media/company/empresa_logo_nuevo.png"
}
```

##### 👁️ Mostrar Logo

- Método: GET
- URL: `http://localhost:8000/api/company/company/1/show_logo/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (con logo):

```json
{
    "has_logo": true,
    "logo_url": "/media/company/empresa_logo.png",
    "logo_url_absolute": "http://localhost:8000/media/company/empresa_logo.png",
    "company_name": "Clínica San José",
    "company_id": 1
}
```

- Respuesta 200 (sin logo):

```json
{
    "has_logo": false,
    "message": "La empresa no tiene logo"
}
```

##### 🗑️ Eliminar Logo

- Método: DELETE
- URL: `http://localhost:8000/api/company/company/1/delete_logo/`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "message": "Logo eliminado correctamente"
}
```

#### 📝 Campos del Modelo Empresa

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | ID único de la empresa |
| `reflexo` | Integer | ID del tenant (empresa) |
| `company_name` | String | Nombre de la empresa |
| `company_logo` | String | URL o ruta del logo |
| `logo_url` | String | URL completa del logo (read-only) |
| `has_logo` | Boolean | Indica si tiene logo (read-only) |
| `created_at` | DateTime | Fecha de creación |
| `updated_at` | DateTime | Fecha de última actualización |

#### 🚨 Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| `400` | Nombre de empresa requerido | Incluir `company_name` en el body |
| `400` | La empresa ya tiene un logo | Usar PUT para actualizar logo existente |
| `400` | Se requiere la URL del logo | Incluir `company_logo` en el body |
| `400` | El logo excede el tamaño máximo | Archivo debe ser menor a 2MB |
| `400` | Formato no permitido | Solo se aceptan: jpg, jpeg, png |
| `400` | El archivo no es una imagen válida | Verificar que el archivo sea una imagen |
| `401` | No autenticado | Verificar token JWT válido |
| `403` | Sin permisos | Verificar permisos de tenant |
| `404` | Empresa no encontrada | Verificar que el ID existe |
| `500` | Error al procesar el logo | Revisar logs del servidor |

#### 📋 Validaciones de Logos

##### ✅ **Formatos permitidos:**
- **Extensiones:** `.jpg`, `.jpeg`, `.png`
- **Tamaño máximo:** 2MB por archivo
- **Validación:** Verificación de integridad de imagen

##### 🔄 **Métodos de subida:**
1. **JSON con URL:** `{"company_logo": "https://ejemplo.com/logo.png"}`
2. **Form-Data con archivo:** Campo `logo_file` con archivo adjunto
3. **Form-Data con company_logo:** Campo `company_logo` con archivo adjunto

##### 🎯 **Comportamiento de endpoints:**
- **POST `/upload_logo/`:** Solo si la empresa NO tiene logo
- **PUT `/upload_logo/`:** Actualiza logo existente
- **GET `/show_logo/`:** Muestra información del logo actual
- **DELETE `/delete_logo/`:** Elimina el logo (no elimina archivo físico)

#### 📋 Validaciones Generales

- **Campo requerido:** `company_name` es obligatorio
- **Multitenant:** Solo se pueden ver/editar empresas del tenant actual
- **Logo único:** Una empresa solo puede tener un logo
- **URLs absolutas:** Los endpoints de logo devuelven URLs completas

---

### 📊 Estadísticas (/api/company/statistics/)

#### 🔗 Endpoints

| Método | Endpoint | Descripción | Autenticación |
|-------:|----------|-------------|---------------|
|    GET | `/api/company/statistics/metricas/` | Obtener métricas generales | Requerida |
|    GET | `/api/company/reports/statistics/` | Obtener estadísticas (alternativo) | Requerida |

> ℹ️ Notas:
> - Ambos endpoints requieren parámetros `start` y `end` con formato `YYYY-MM-DD`.
> - Si `start > end` devuelve 400.
> - Formato de fecha inválido devuelve 400.
> - Filtrado por tenant automáticamente.

#### 🧪 Ejemplos de Estadísticas

##### 📊 Estadísticas de Datos

- Método: GET
- URL: `http://localhost:8000/api/company/reports/statistics/?start=2025-08-25&end=2025-08-28`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
{
    "terapeutas": [
        {
            "id": 1,
            "terapeuta": "Rodríguez Martínez, Carlos",
            "sesiones": 2,
            "ingresos": 150,
            "raiting": 5
        }
    ],
    "tipos_pago": {
        "Efectivo": 1,
        "Yape": 1
    },
    "metricas": {
        "ttlpacientes": 2,
        "ttlsesiones": 2,
        "ttlganancias": 150
    },
    "ingresos": {
        "Lunes": 150
    },
    "sesiones": {
        "Lunes": 2
    },
    "tipos_pacientes": {
        "c": 0,
        "cc": 0
    }
}
```

**Nota Importante sobre Estadísticas:**
- **Debe existir lo necesario**: Se debe haber ingresado datos como ingresos, citas, cant. de tipo de pacientes, terapeutas, etc.

#### 📋 Parámetros Requeridos

| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `start` | String | Fecha inicio (YYYY-MM-DD) | `2025-01-01` |
| `end` | String | Fecha fin (YYYY-MM-DD) | `2025-01-31` |

---

### 📈 Reportes JSON (/api/company/reports/)

> **Nota Importante:** Para que los reportes muestren datos correctos, al crear la cita incluir `payment`, `payment_type` y `payment_type_name` (cuando aplique).

#### 🔗 Endpoints

| Método | Endpoint | Descripción | Autenticación |
|-------:|----------|-------------|---------------|
| **GET** | `/api/company/reports/appointments-per-therapist/?date=YYYY-MM-DD` | Reporte por terapeuta (por día) | Requerida |
| **GET** | `/api/company/reports/daily-cash/?date=YYYY-MM-DD` | Caja diaria (pagos del día) | Requerida |
| **GET** | `/api/company/reports/patients-by-therapist/?date=YYYY-MM-DD` | Pacientes por terapeuta (por día) | Requerida |
| **GET** | `/api/company/reports/appointments-between-dates/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` | Citas entre fechas | Requerida |
| **GET** | `/api/company/exports/excel/citas-rango/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` | Generar reporte en Excel | Requerida |

#### 🧪 Ejemplos de Reportes

##### 📅 Citas por Terapeuta

- Método: GET
- URL: `http://localhost:8000/api/company/reports/appointments-per-therapist/?date=2025-08-25`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`
  - `Content-Type: application/json`

- Respuesta 200 (ejemplo):

```json
{
    "therapists_appointments": [
        {
            "id": 1,
            "first_name": "Carlos",
            "last_name_paternal": "Rodríguez",
            "last_name_maternal": "Martínez",
            "appointments_count": 2,
            "percentage": 100
        }
    ],
    "total_appointments_count": 2
}
```

**Nota Importante sobre Citas por terapeuta:**
- **No hay cita creada**: Se debe crear antes una cita para mostrar un reporte.

##### 💰 Caja Diaria

- Método: GET
- URL: `http://localhost:8000/api/company/reports/daily-cash/?date=2025-08-25`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`
  - `Content-Type: application/json`

- Respuesta 200 (ejemplo):

```json
[
    {
        "id_cita": 2,
        "payment": "50.00",
        "payment_type": 2,
        "payment_type_name": "Efectivo"
    },
    {
        "id_cita": 1,
        "payment": "100.00",
        "payment_type": 1,
        "payment_type_name": "Yape"
    }
]
```

**Nota Importante sobre Reporte diario de caja:**
- **`payment_type`**: Se debe crear antes generar un reporte diario de caja.

##### 👥 Pacientes por Terapeuta

- Método: GET
- URL: `http://localhost:8000/api/company/reports/patients-by-therapist/?date=2025-08-25`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`
  - `Content-Type: application/json`

- Respuesta 200 (ejemplo):

```json
[
    {
        "therapist_id": "1",
        "therapist": "Rodríguez Martínez Carlos",
        "patients": [
            {
                "patient_id": 2,
                "patient": "García Hernández Jose Sofía",
                "appointments": 1
            },
            {
                "patient_id": 1,
                "patient": "García Hernández Ana Sofía",
                "appointments": 1
            }
        ]
    }
]
```

**Nota Importante sobre Reporte de pacientes por Terapeuta:**
- **`therapist`**: Debe estar agregado a una cita.
- **`patient`**: Debe estar agregado a una cita y relacionado con un terapeuta.

##### 📋 Citas entre Fechas

- Método: GET
- URL: `http://localhost:8000/api/company/reports/appointments-between-dates/?start_date=2025-08-25&end_date=2025-08-28`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta 200 (ejemplo):

```json
[
    {
        "appointment_id": 1,
        "patient_id": 1,
        "document_number_patient": "11111111",
        "patient": "García Hernández Ana Sofía",
        "primary_phone_patient": "+51 444 444 444",
        "appointment_date": "2025-08-25",
        "appointment_hour": "14:30"
    },
    {
        "appointment_id": 2,
        "patient_id": 1,
        "document_number_patient": "11111111",
        "patient": "García Hernández Ana Sofía",
        "primary_phone_patient": "+51 444 444 444",
        "appointment_date": "2025-08-25",
        "appointment_hour": "14:30"
    }
]
```

**Nota Importante sobre Reporte de Citas entre Fechas:**
- **Debe contener lo necesario**: De haber un paciente, una fecha exacta de la cita y también una hora de la cita.

##### 📊 Generar Reporte en Excel

- Método: GET
- URL: `http://localhost:8000/api/company/exports/excel/citas-rango/?start_date=2025-08-25&end_date=2025-08-28`
- Headers:
  - `Authorization: Bearer <jwt_access_token>`

- Respuesta: Archivo Excel descargable

**Ejemplo del contenido del Excel:**
```
ID Paciente	DNI/Documento	Paciente	      Teléfono	      Fecha	   Hora
1	11111111	García Hernández Ana Sofía	+51 444 444 444	2025-08-25	14:30
1	11111111	García Hernández Ana Sofía	+51 444 444 444	2025-08-25	14:30
```

**Nota Importante sobre Excel:**
- **Usar el endpoint en un navegador** ya que si se pone en el Postman no se ve de una manera adecuada.

#### 📋 Parámetros por Endpoint

| Endpoint | Parámetros Requeridos | Descripción |
|----------|----------------------|-------------|
| `appointments-per-therapist` | `date` | Fecha específica (YYYY-MM-DD) |
| `daily-cash` | `date` | Fecha específica (YYYY-MM-DD) |
| `patients-by-therapist` | `date` | Fecha específica (YYYY-MM-DD) |
| `appointments-between-dates` | `start_date`, `end_date` | Rango de fechas (YYYY-MM-DD) |
| `exports/excel/citas-rango` | `start_date`, `end_date` | Rango de fechas (YYYY-MM-DD) |

---

### 📄 Exportaciones (/api/company/exports/)

Las exportaciones vuelven a estar disponibles.

#### 🔗 Endpoints PDF

| Método | Endpoint | Descripción | Autenticación |
|-------:|----------|-------------|---------------|
| **GET** | `/api/company/exports/pdf/citas-terapeuta/` | PDF: Citas por terapeuta | Requerida |
| **GET** | `/api/company/exports/pdf/pacientes-terapeuta/` | PDF: Pacientes por terapeuta | Requerida |
| **GET** | `/api/company/exports/pdf/resumen-caja/` | PDF: Resumen de caja | Requerida |
| **GET** | `/api/company/exports/pdf/caja-chica-mejorada/` | PDF: Caja chica mejorada | Requerida |
| **GET** | `/api/company/exports/pdf/tickets-pagados/` | PDF: Tickets pagados | Requerida |

#### 🔗 Endpoints Excel

| Método | Endpoint | Descripción | Autenticación |
|-------:|----------|-------------|---------------|
| **GET** | `/api/company/exports/excel/citas-rango/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` | Excel: Citas en rango | Requerida |
| **GET** | `/api/company/exports/excel/caja-chica-mejorada/?date=YYYY-MM-DD` | Excel: Caja chica mejorada | Requerida |
| **GET** | `/api/company/exports/excel/tickets-pagados/?date=YYYY-MM-DD` | Excel: Tickets pagados | Requerida |

