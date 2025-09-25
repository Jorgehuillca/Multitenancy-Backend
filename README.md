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
