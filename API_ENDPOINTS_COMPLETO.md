# 🔌 API Endpoints Completo - Backend Reflexo MTV

## 🌐 Base URL
```
http://localhost:8000/  # Desarrollo local
```

## 📋 Estándar de URLs Unificado
Todas las APIs siguen el patrón: `/api/[modulo]/[recurso]/`

---

## 🏗️ Módulo 1: Arquitectura y Autenticación (`/api/architect/`)

### Autenticación
| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| **POST** | `/api/architect/auth/login/` | Login de usuario | No requerida |
| **POST** | `/api/architect/auth/register/` | Registro de usuario | No requerida |

#### Ejemplos de Autenticación

**Login de Usuario:**
- **Método:** POST
- **URL:** `{{base_url}}/api/architect/auth/login/`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "email": "xxangelx31@gmail.com",
    "password": "edu123"
  }
  ```

**Respuesta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 3,
    "username": "edu",
    "email": "xxangelx31@gmail.com",
    "is_active": true
  }
}
```

**Registro de Usuario:**
- **Método:** POST
- **URL:** `{{base_url}}/api/architect/auth/register/`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "username": "nuevo_usuario",
    "email": "nuevo@ejemplo.com",
    "password": "MiContraseña123!",
    "password_confirm": "MiContraseña123!"
  }
  ```

**Respuesta Exitosa:**
```json
{
  "id": 4,
  "username": "nuevo_usuario",
  "email": "nuevo@ejemplo.com",
  "is_active": true,
  "date_joined": "2025-08-21T18:30:00Z"
}
```

**Posibles Errores:**
```json
{
  "password": [
    "Esta contraseña es demasiado común. Elige una contraseña más segura."
  ]
}
```
```json
{
  "password_confirm": [
    "Las contraseñas no coinciden"
  ]
}
```
```json
{
  "email": [
    "Este campo es requerido."
  ],
  "username": [
    "Este campo es requerido."
  ]
}
```

### Usuarios
| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| **GET** | `/api/architect/users/` | Listar usuarios | Requerida |
| **POST** | `/api/architect/users/` | Crear usuario | Requerida |

#### Ejemplos de Usuarios

**Listar Usuarios:**
- **Método:** GET
- **URL:** `{{base_url}}/api/architect/users/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`

**Respuesta:**
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 2,
      "username": "admin",
      "email": "admin@example.com",
      "is_active": true,
      "rol": "Admin"
    },
    {
      "id": 3,
      "username": "edu",
      "email": "xxangelx31@gmail.com",
      "is_active": true,
      "rol": "User"
    }
  ]
}
```

**Crear Usuario:**
- **Método:** POST
- **URL:** `{{base_url}}/api/architect/users/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "username": "nuevo_admin",
    "email": "admin2@ejemplo.com",
    "password": "Admin123!",
    "first_name": "Juan",
    "last_name": "Administrador",
    "is_staff": true,
    "is_superuser": false
  }
  ```

**Respuesta Exitosa:**
```json
{
  "id": 5,
  "username": "nuevo_admin",
  "email": "admin2@ejemplo.com",
  "first_name": "Juan",
  "last_name": "Administrador",
  "is_active": true,
  "is_staff": true,
  "is_superuser": false,
  "date_joined": "2025-08-21T19:00:00Z"
}
```

**Posibles Errores:**
```json
{
  "email": [
    "Este campo es requerido."
  ],
  "username": [
    "Este campo es requerido."
  ]
}
```
```json
{
  "email": [
    "Ya existe un usuario con este email."
  ]
}
```
```json
{
  "username": [
    "Ya existe un usuario con este nombre de usuario."
  ]
}
```

---

## 👤 Módulo 2: Perfiles de Usuarios (`/api/profiles/`)

### Gestión de Usuario
| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| **GET** | `/api/profiles/users/me/` | Mi perfil de usuario | Requerida |
| **PUT** | `/api/profiles/users/me/update/` | Actualizar mi perfil | Requerida |
| **POST** | `/api/profiles/users/me/photo/` | Subir foto de perfil | Requerida |
| **GET** | `/api/profiles/users/search/` | Buscar usuarios | Requerida |
| **GET** | `/api/profiles/users/profile/` | Ver mi perfil completo | Requerida |

#### Ejemplos de Perfiles

**Obtener Mi Perfil:**
- **Método:** GET
- **URL:** `{{base_url}}/api/profiles/users/me/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`

**Respuesta:**
```json
{
  "id": 3,
  "username": "edu",
  "email": "xxangelx31@gmail.com",
  "first_name": "Eduardo",
  "last_name": "Pérez",
  "full_name": "Eduardo Pérez",
  "phone": "+51 999 999 999",
  "rol": "User",
  "is_active": true,
  "date_joined": "2025-08-21T15:30:00Z",
  "last_login": "2025-08-21T18:30:00Z",
  "profile_photo_url": "http://localhost:8000/media/profile_photos/foto_perfil.jpg"
}
```

**Actualizar Mi Perfil:**
- **Método:** PUT
- **URL:** `{{base_url}}/api/profiles/users/me/update/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "first_name": "Eduardo",
    "last_name": "García",
    "phone": "+51 888 888 888"
  }
  ```

**Respuesta Exitosa:**
```json
{
  "id": 3,
  "username": "edu",
  "email": "xxangelx31@gmail.com",
  "first_name": "Eduardo",
  "last_name": "García",
  "full_name": "Eduardo García",
  "phone": "+51 888 888 888",
  "rol": "User",
  "is_active": true,
  "date_joined": "2025-08-21T15:30:00Z",
  "last_login": "2025-08-21T18:30:00Z",
  "profile_photo_url": "http://localhost:8000/media/profile_photos/foto_perfil.jpg"
}
```

**Subir Foto de Perfil:**
- **Método:** POST
- **URL:** `{{base_url}}/api/profiles/users/me/photo/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: multipart/form-data
  ```
- **Body (form-data):**
  ```
  profile_photo: [archivo de imagen]
  ```
  - **Key:** `profile_photo`
  - **Type:** File
  - **Value:** Seleccionar archivo de imagen (JPG, PNG, etc.)

**Respuesta Exitosa:**
```json
{
  "id": 3,
  "username": "edu",
  "email": "xxangelx31@gmail.com"
}
```

**Posibles Errores:**
```json
{
  "profile_photo": [
    "Este campo es requerido."
  ]
}
```
```json
{
  "profile_photo": [
    "Sube un archivo válido. El archivo que subiste está vacío o no es una imagen válida."
  ]
}
```

**Ver Mi Perfil Completo:**
- **Método:** GET
- **URL:** `{{base_url}}/api/profiles/users/profile/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`

**Respuesta:**
```json
{
  "id": 3,
  "username": "edu",
  "email": "xxangelx31@gmail.com",
  "first_name": "Eduardo",
  "last_name": "Pérez",
  "full_name": "Eduardo Pérez",
  "phone": "+51 999 999 999",
  "rol": "User",
  "is_active": true,
  "date_joined": "2025-08-21T15:30:00Z",
  "last_login": "2025-08-21T18:30:00Z",
  "profile_photo_url": "http://localhost:8000/media/profile_photos/foto_perfil.jpg"
}
```

**Buscar Usuarios:**
- **Método:** GET
- **URL:** `{{base_url}}/api/profiles/users/search/?q=edu`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`

---

## 🩺 Módulo 3: Pacientes y Diagnósticos (`/api/patients/`)

### Pacientes
| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| **GET** | `/api/patients/patients/` | Listar pacientes | Requerida |
| **POST** | `/api/patients/patients/` | Crear paciente | Requerida |
| **GET** | `/api/patients/patients/1/` | Ver paciente específico | Requerida |
| **PUT** | `/api/patients/patients/{id}/` | Actualizar paciente | Requerida |
| **DELETE** | `/api/patients/patients/{id}/` | Eliminar paciente | Requerida |
| **GET** | `/api/patients/patients/search/` | Buscar pacientes | Requerida |

#### Ejemplos de Pacientes

**Listar Pacientes:**
- **Método:** GET
- **URL:** `{{base_url}}/api/patients/patients/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`

**Respuesta:**
```json
[
  {
    "id": 1,
    "document_number": "12345678",
    "full_name": "María González López",
    "age": 33,
    "sex": "F",
    "primary_phone": "+51 777 777 777",
    "email": "maria@ejemplo.com",
    "region_name": "Lima",
    "document_type_name": "DNI",
    "created_at": "2025-08-21T15:00:00Z"
  }
]
```

**Crear Paciente:**
- **Método:** POST
- **URL:** `{{base_url}}/api/patients/patients/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "document_number": "11111111",
    "paternal_lastname": "García",
    "maternal_lastname": "Hernández",
    "name": "Ana Sofía",
    "birth_date": "1995-12-03",
    "sex": "F",
    "primary_phone": "+51 444 444 444",
    "email": "ana.sofia@ejemplo.com",
    "address": "Calle Nueva 123",
    "region_id": 1,
    "province_id": 1,
    "district_id": 1,
    "document_type_id": 1
  }
  ```

**Respuesta Exitosa:**
```json
{
  "id": 2,
  "document_number": "87654321",
  "paternal_lastname": "López",
  "maternal_lastname": "García",
  "name": "Juan Carlos",
  "personal_reference": null,
  "birth_date": "1985-03-20",
  "sex": "M",
  "primary_phone": "+51 666 666 666",
  "secondary_phone": null,
  "email": "juan@ejemplo.com",
  "ocupation": null,
  "health_condition": null,
  "address": "Calle Secundaria 456",
  "region": {
    "id": 1,
    "name": "Lima",
    "ubigeo_code": "15"
  },
  "province": {
    "id": 1,
    "name": "Lima",
    "ubigeo_code": "1501"
  },
  "district": {
    "id": 1,
    "name": "Lima",
    "ubigeo_code": "150101"
  },
  "document_type": {
    "id": 1,
    "name": "DNI",
    "description": "Documento Nacional de Identidad"
  },
  "created_at": "2025-08-21T19:00:00Z",
  "updated_at": "2025-08-21T19:00:00Z"
}
```

**Ejemplos Adicionales de Datos Únicos:**

**Ejemplo 2:**
```json
{
  "document_number": "22222222",
  "paternal_lastname": "López",
  "maternal_lastname": "Morales",
  "name": "Roberto Carlos",
  "birth_date": "1988-04-18",
  "sex": "M",
  "primary_phone": "+51 333 333 333",
  "email": "roberto.carlos@ejemplo.com",
  "address": "Av. Libertad 456",
  "region_id": 1,
  "province_id": 1,
  "district_id": 1,
  "document_type_id": 1
}
```

**Ejemplo 3:**
```json
{
  "document_number": "33333333",
  "paternal_lastname": "Ramírez",
  "maternal_lastname": "Vargas",
  "name": "María Elena",
  "birth_date": "1990-09-25",
  "sex": "F",
  "primary_phone": "+51 222 222 222",
  "email": "maria.elena@ejemplo.com",
  "address": "Jr. San Martín 789",
  "region_id": 1,
  "province_id": 1,
  "district_id": 1,
  "document_type_id": 1
}
```

**Posibles Errores de Validación:**
```json
{
  "document_number": [
    "El número de documento ya está registrado."
  ],
  "email": [
    "El correo electrónico ya está registrado."
  ]
}
```
```json
{
  "document_number": [
    "Este campo es requerido."
  ],
  "name": [
    "Este campo es requerido."
  ],
  "paternal_lastname": [
    "Este campo es requerido."
  ]
}
```
```json
{
  "birth_date": [
    "La fecha de nacimiento no puede ser en el futuro."
  ]
}
```

**Ver Paciente Específico:**
- **Método:** GET
- **URL:** `{{base_url}}/api/patients/patients/1/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`

**Respuesta:**
```json
{
  "id": 1,
  "document_number": "12345678",
  "paternal_lastname": "González",
  "maternal_lastname": "López",
  "name": "María",
  "personal_reference": null,
  "birth_date": "1990-05-15",
  "sex": "F",
  "primary_phone": "+51 777 777 777",
  "secondary_phone": null,
  "email": "maria@ejemplo.com",
  "ocupation": null,
  "health_condition": null,
  "address": "Av. Principal 123",
  "region": {
    "id": 1,
    "name": "Lima",
    "ubigeo_code": "15"
  },
  "province": {
    "id": 1,
    "name": "Lima",
    "ubigeo_code": "1501"
  },
  "district": {
    "id": 1,
    "name": "Lima",
    "ubigeo_code": "150101"
  },
  "document_type": {
    "id": 1,
    "name": "DNI",
    "description": "Documento Nacional de Identidad"
  },
  "created_at": "2025-08-21T15:00:00Z",
  "updated_at": "2025-08-21T15:00:00Z"
}
```

**Actualizar Paciente:**
- **Método:** PUT
- **URL:** `{{base_url}}/api/patients/patients/1/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "document_number": "12345678",
    "paternal_lastname": "González",
    "maternal_lastname": "López",
    "name": "María Elena",
    "birth_date": "1990-05-15",
    "sex": "F",
    "primary_phone": "+51 777 777 777",
    "email": "maria.actualizada@ejemplo.com",
    "address": "Av. Principal 123, Lima",
    "region_id": 1,
    "province_id": 1,
    "district_id": 1,
    "document_type_id": 1
  }
  ```

**Respuesta Exitosa:**
```json
{
  "id": 1,
  "document_number": "12345678",
  "paternal_lastname": "González",
  "maternal_lastname": "López",
  "name": "María Elena",
  "personal_reference": null,
  "birth_date": "1990-05-15",
  "sex": "F",
  "primary_phone": "+51 777 777 777",
  "secondary_phone": null,
  "email": "maria.actualizada@ejemplo.com",
  "ocupation": null,
  "health_condition": null,
  "address": "Av. Principal 123, Lima",
  "region": {
    "id": 1,
    "name": "Lima",
    "ubigeo_code": "15"
  },
  "province": {
    "id": 1,
    "name": "Lima",
    "ubigeo_code": "1501"
  },
  "district": {
    "id": 1,
    "name": "Lima",
    "ubigeo_code": "150101"
  },
  "document_type": {
    "id": 1,
    "name": "DNI",
    "description": "Documento Nacional de Identidad"
  },
  "created_at": "2025-08-21T15:00:00Z",
  "updated_at": "2025-08-21T19:30:00Z"
}
```

**Posibles Errores de Actualización:**
```json
{
  "document_number": [
    "El número de documento ya está registrado por otro paciente."
  ]
}
```
```json
{
  "email": [
    "El correo electrónico ya está registrado por otro paciente."
  ]
}
```
```json
{
  "birth_date": [
    "La fecha de nacimiento no puede ser en el futuro."
  ]
}
```

**Buscar Pacientes:**
- **Método:** GET
- **URL:** `{{base_url}}/api/patients/patients/search/?q=maria`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`

**Eliminar Paciente:**
- **Método:** DELETE
- **URL:** `{{base_url}}/api/patients/patients/1/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`

**Respuesta Exitosa:**
```
Status: 204 No Content
Body: (vacío)
```

**Nota Importante sobre IDs:**
- Reemplaza `{id}` con el número real del ID del paciente
- Ejemplo: Para ver el paciente con ID 2, usa: `/api/patients/patients/2/`
- Para ver el paciente con ID 5, usa: `/api/patients/patients/5/`
- Para actualizar el paciente con ID 3, usa: `/api/patients/patients/3/`
- Para eliminar el paciente con ID 4, usa: `/api/patients/patients/4/`
- **NO uses** `/api/patients/patients/{id}/` literalmente

### Diagnósticos
| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| **GET** | `/api/patients/diagnoses/` | Listar diagnósticos | Requerida |
| **POST** | `/api/patients/diagnoses/` | Crear diagnóstico | Requerida |
| **GET** | `/api/patients/diagnoses/{id}/` | Ver diagnóstico específico | Requerida |
| **PUT** | `/api/patients/diagnoses/{id}/` | Actualizar diagnóstico | Requerida |
| **DELETE** | `/api/patients/diagnoses/{id}/` | Eliminar diagnóstico | Requerida |
| **GET** | `/api/patients/diagnoses/search/` | Buscar diagnósticos | Requerida |

#### Ejemplos de Diagnósticos

**Crear Diagnóstico:**
- **Método:** POST
- **URL:** `{{base_url}}/api/patients/diagnoses/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "code": "D001",
    "name": "Dolor lumbar crónico",
    "description": "Dolor persistente en la zona lumbar que puede irradiarse a las piernas"
  }
  ```

**Respuesta Exitosa:**
```json
{
  "id": 1,
  "code": "D001",
  "name": "Dolor lumbar crónico",
  "description": "Dolor persistente en la zona lumbar que puede irradiarse a las piernas",
  "created_at": "2025-08-21T16:00:00Z",
  "updated_at": "2025-08-21T16:00:00Z"
}
```

**Ejemplos Adicionales de Diagnósticos:**

**Ejemplo 2:**
```json
{
  "code": "D002",
  "name": "Cefalea tensional",
  "description": "Dolor de cabeza causado por tensión muscular en cuello y hombros"
}
```

**Ejemplo 3:**
```json
{
  "code": "D003",
  "name": "Artritis reumatoide",
  "description": "Enfermedad inflamatoria crónica que afecta las articulaciones"
}
```

**Actualizar Diagnóstico:**
- **Método:** PUT
- **URL:** `{{base_url}}/api/patients/diagnoses/1/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "code": "D001",
    "name": "Dolor lumbar crónico - Actualizado",
    "description": "Dolor persistente en la zona lumbar que puede irradiarse a las piernas. Diagnóstico actualizado con nueva información."
  }
  ```

**Respuesta Exitosa:**
```json
{
  "id": 1,
  "code": "D001",
  "name": "Dolor lumbar crónico - Actualizado",
  "description": "Dolor persistente en la zona lumbar que puede irradiarse a las piernas. Diagnóstico actualizado con nueva información.",
  "created_at": "2025-08-21T16:00:00Z",
  "updated_at": "2025-08-21T19:30:00Z"
}
```

**Posibles Errores de Validación:**
```json
{
  "code": [
    "Este campo es requerido."
  ],
  "name": [
    "Este campo es requerido."
  ]
}
```
```json
{
  "code": [
    "Ya existe un diagnóstico con este código."
  ]
}
```
```json
{
  "code": [
    "El código solo debe contener letras y números."
  ]
}
```
```json
{
  "code": [
    "El código no debe superar los 10 caracteres."
  ]
}
```

**Buscar Diagnósticos:**
- **Método:** GET
- **URL:** `{{base_url}}/api/patients/diagnoses/search/?q=dolor`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`

**Respuesta Exitosa:**
```json
[
  {
    "id": 1,
    "code": "D001",
    "name": "Dolor lumbar crónico",
    "description": "Dolor persistente en la zona lumbar que puede irradiarse a las piernas",
    "created_at": "2025-08-21T16:00:00Z"
  }
]
```

**Posibles Errores:**
```json
{
  "detail": "Se requiere un parámetro de búsqueda."
}
```

**Nota Importante sobre Búsqueda:**
- **Parámetro obligatorio**: `q` (query de búsqueda)
- **Ejemplos de uso**:
  - Buscar por código: `?q=D001`
  - Buscar por nombre: `?q=dolor`
  - Buscar por descripción: `?q=lumbar`
- **NO uses** `/api/patients/diagnoses/search/` sin el parámetro `q`

---

## 👨‍⚕️ Módulo 4: Terapeutas (`/api/therapists/`)

### Terapeutas
| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| **GET** | `/api/therapists/therapists/` | Listar terapeutas | Requerida |
| **POST** | `/api/therapists/therapists/` | Crear terapeuta | Requerida |
| **GET** | `/api/therapists/therapists/{id}/` | Ver terapeuta específico | Requerida |
| **PUT** | `/api/therapists/therapists/{id}/` | Actualizar terapeuta | Requerida |
| **PATCH** | `/api/therapists/therapists/{id}/` | Actualizar parcialmente | Requerida |
| **DELETE** | `/api/therapists/therapists/{id}/` | Soft delete terapeuta | Requerida |
| **GET** | `/api/therapists/therapists/inactive/` | Terapeutas inactivos | Requerida |
| **POST** | `/api/therapists/therapists/{id}/restore/` | Restaurar terapeuta | Requerida |

#### Ejemplos de Terapeutas

**Listar Terapeutas:**
- **Método:** GET
- **URL:** `{{base_url}}/api/therapists/therapists/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`

**Respuesta:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "document_type_id": "1",
      "document_number": "12345678",
      "first_name": "Ana",
      "last_name_paternal": "García",
      "last_name_maternal": "López",
      "birth_date": "1990-01-01",
      "gender": "F",
      "phone": "999999999",
      "email": "ana@gmail.com",
      "address": "Av. Siempre Viva 123",
      "is_active": true,
      "region_fk": {
        "id": 1,
        "name": "Lima",
        "ubigeo_code": "15"
      },
      "province_fk": {
        "id": 1,
        "name": "Lima",
        "ubigeo_code": "1501"
      },
      "district_fk": {
        "id": 1,
        "name": "Lima",
        "ubigeo_code": "150101"
      }
    }
  ]
}
```

**Crear Terapeuta:**
- **Método:** POST
- **URL:** `{{base_url}}/api/therapists/therapists/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "document_type_id": "1",
    "document_number": "87654321",
    "first_name": "Carlos",
    "last_name_paternal": "Rodríguez",
    "last_name_maternal": "Martínez",
    "birth_date": "1988-07-15",
    "gender": "M",
    "phone": "888888888",
    "email": "carlos@gmail.com",
    "address": "Calle Principal 456",
    "region_fk_id": 1,
    "province_fk_id": 1,
    "district_fk_id": 1
  }
  ```

**Buscar Terapeutas:**
- **Método:** GET
- **URL:** `{{base_url}}/api/therapists/therapists/?search=ana`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`

**Filtrar por Región:**
- **Método:** GET
- **URL:** `{{base_url}}/api/therapists/therapists/?region=1`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`

**Actualizar Terapeuta:**
- **Método:** PUT
- **URL:** `{{base_url}}/api/therapists/therapists/1/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "document_type_id": "1",
    "document_number": "12345678",
    "first_name": "Ana María",
    "last_name_paternal": "García",
    "last_name_maternal": "López",
    "birth_date": "1990-01-01",
    "gender": "F",
    "phone": "999999999",
    "email": "ana.actualizada@gmail.com",
    "address": "Av. Siempre Viva 123, Lima",
    "region_fk_id": 1,
    "province_fk_id": 1,
    "district_fk_id": 1
  }
  ```

**Respuesta Exitosa:**
```json
{
  "id": 1,
  "document_type_id": "1",
  "document_number": "12345678",
  "first_name": "Ana María",
  "last_name_paternal": "García",
  "last_name_maternal": "López",
  "birth_date": "1990-01-01",
  "gender": "F",
  "phone": "999999999",
  "email": "ana.actualizada@gmail.com",
  "address": "Av. Siempre Viva 123, Lima",
  "is_active": true,
  "region_fk": {
    "id": 1,
    "name": "Lima",
    "ubigeo_code": "15"
  },
  "province_fk": {
    "id": 1,
    "name": "Lima",
    "ubigeo_code": "1501"
  },
  "district_fk": {
    "id": 1,
    "name": "Lima",
    "ubigeo_code": "150101"
  },
  "created_at": "2025-08-21T16:00:00Z",
  "updated_at": "2025-08-21T19:30:00Z"
}
```

**Posibles Errores de Actualización:**
```json
{
  "document_number": [
    "Ya existe un terapeuta con este número de documento."
  ]
}
```json
{
  "document_tyoe_id": [
    "El tipo de documento seleccionado no existe."
  ]
}
```json
{
  "email": [
    "Ya existe un terapeuta con este email."
  ]
}
```
```json
{
  "birth_date": [
    "La fecha de nacimiento no puede ser en el futuro."
  ]
}
```

**Restaurar Terapeuta:**
- **Método:** POST
- **URL:** `{{base_url}}/api/therapists/therapists/1/restore/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {}
  ```

**Respuesta Exitosa:**
```json
{
  "id": 1,
  "document_type_id": "1",
  "document_number": "12345678",
  "first_name": "Ana María",
  "last_name_paternal": "García",
  "last_name_maternal": "López",
  "birth_date": "1990-01-01",
  "gender": "F",
  "phone": "999999999",
  "email": "ana.actualizada@gmail.com",
  "address": "Av. Siempre Viva 123, Lima",
  "is_active": true,
  "region_fk": {
    "id": 1,
    "name": "Lima",
    "ubigeo_code": "15"
  },
  "province_fk": {
    "id": 1,
    "name": "Lima",
    "ubigeo_code": "1501"
  },
  "district_fk": {
    "id": 1,
    "name": "Lima",
    "ubigeo_code": "150101"
  },
  "created_at": "2025-08-21T16:00:00Z",
  "updated_at": "2025-08-21T19:30:00Z"
}
```

**Posibles Errores:**
```json
{
  "detail": "El terapeuta ya está activo."
}
```
```json
{
  "detail": "Terapeuta no encontrado."
}
```

**Nota Importante sobre Restauración:**
- **Solo funciona** con terapeutas que han sido eliminados (soft delete)
- **No requiere datos** en el body, solo el ID en la URL
- **Cambia `is_active`** de `false` a `true`
- **Mantiene** todos los datos originales del terapeuta

### Especialidades
| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| **GET** | `/api/therapists/specializations/` | Listar especialidades | Requerida |
| **POST** | `/api/therapists/specializations/` | Crear especialidad | Requerida |
| **GET** | `/api/therapists/specializations/{id}/` | Ver especialidad | Requerida |
| **PUT** | `/api/therapists/specializations/{id}/` | Actualizar especialidad | Requerida |
| **PATCH** | `/api/therapists/specializations/{id}/` | Actualizar parcialmente | Requerida |
| **DELETE** | `/api/therapists/specializations/{id}/` | Eliminar especialidad | Requerida |

#### Ejemplos de Especialidades

**Crear Especialidad:**
- **Método:** POST
- **URL:** `{{base_url}}/api/therapists/specializations/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "name": "Fisioterapia Deportiva",
    "description": "Especialidad en rehabilitación deportiva",
    "is_active": true
  }
  ```

**Respuesta:**
```json
{
  "id": 1,
  "name": "Fisioterapia Deportiva",
  "description": "Especialidad en rehabilitación deportiva",
  "is_active": true,
  "created_at": "2025-08-21T16:30:00Z"
}
```

**Actualizar Especialidad:**
- **Método:** PUT
- **URL:** `{{base_url}}/api/therapists/specializations/1/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "name": "Fisioterapia Deportiva - Actualizada",
    "description": "Especialidad en rehabilitación deportiva y medicina del deporte. Incluye tratamiento de lesiones deportivas y prevención de lesiones.",
    "is_active": true
  }
  ```

**Respuesta Exitosa:**
```json
{
  "id": 1,
  "name": "Fisioterapia Deportiva - Actualizada",
  "description": "Especialidad en rehabilitación deportiva y medicina del deporte. Incluye tratamiento de lesiones deportivas y prevención de lesiones.",
  "is_active": true,
  "created_at": "2025-08-21T16:30:00Z",
  "updated_at": "2025-08-21T19:30:00Z"
}
```

**Posibles Errores de Actualización:**
```json
{
  "name": [
    "Este campo es requerido."
  ]
}
```
```json
{
  "name": [
    "Ya existe una especialidad con este nombre."
  ]
}
```
```json
{
  "description": [
    "La descripción no puede estar vacía."
  ]
}
```

### Ubicaciones Geográficas

#### Regiones
| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| **GET** | `/api/therapists/regions/` | Listar regiones | No requerida |
| **GET** | `/api/therapists/regions/{id}/` | Ver región específica | No requerida |

#### Provincias
| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| **GET** | `/api/therapists/provinces/` | Listar provincias | No requerida |
| **GET** | `/api/therapists/provinces/{id}/` | Ver provincia | No requerida |

#### Distritos
| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| **GET** | `/api/therapists/districts/` | Listar distritos | No requerida |
| **GET** | `/api/therapists/districts/{id}/` | Ver distrito | No requerida |

#### Ejemplos de Ubicaciones

**Listar Regiones (sin autenticación):**
- **Método:** GET
- **URL:** `{{base_url}}/api/therapists/regions/`
- **Auth:** No requerida

**Respuesta:**
```json
[
  {
    "id": 1,
    "name": "Lima",
    "ubigeo_code": "15"
  },
  {
    "id": 2,
    "name": "Arequipa",
    "ubigeo_code": "04"
  }
]
```

**Filtrar Provincias por Región:**
- **Método:** GET
- **URL:** `{{base_url}}/api/therapists/provinces/?region=1`
- **Auth:** No requerida

**Filtrar Distritos por Provincia:**
- **Método:** GET
- **URL:** `{{base_url}}/api/therapists/districts/?province=1`
- **Auth:** No requerida

---

## 📅 Módulo 5: Citas y Estados (`/api/appointments/`)

### Estados de Citas
| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| **GET** | `/api/appointments/appointment-statuses/` | Listar estados | Requerida |
| **POST** | `/api/appointments/appointment-statuses/` | Crear estado | Requerida |
| **GET** | `/api/appointments/appointment-statuses/{id}/` | Ver estado específico | Requerida |
| **PUT** | `/api/appointments/appointment-statuses/{id}/` | Actualizar estado | Requerida |
| **DELETE** | `/api/appointments/appointment-statuses/{id}/` | Eliminar estado | Requerida |
| **GET** | `/api/appointments/appointment-statuses/active/` | Estados activos | Requerida |
| **POST** | `/api/appointments/appointment-statuses/{id}/activate/` | Activar estado | Requerida |
| **POST** | `/api/appointments/appointment-statuses/{id}/deactivate/` | Desactivar estado | Requerida |
| **GET** | `/api/appointments/appointment-statuses/{id}/appointments/` | Citas por estado | Requerida |

#### Ejemplos de Estados de Citas

**Listar Estados de Citas:**
- **Método:** GET
- **URL:** `{{base_url}}/api/appointments/appointment-statuses/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`

**Respuesta:**
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Pendiente",
      "description": "Cita programada pero no confirmada",
      "is_active": true,
      "created_at": "2025-08-21T10:00:00Z"
    },
    {
      "id": 2,
      "name": "Confirmada",
      "description": "Cita confirmada por el paciente",
      "is_active": true,
      "created_at": "2025-08-21T10:00:00Z"
    },
    {
      "id": 3,
      "name": "Completada",
      "description": "Cita completada exitosamente",
      "is_active": true,
      "created_at": "2025-08-21T10:00:00Z"
    },
    {
      "id": 4,
      "name": "Cancelada",
      "description": "Cita cancelada",
      "is_active": true,
      "created_at": "2025-08-21T10:00:00Z"
    }
  ]
}
```

**Crear Nuevo Estado:**
- **Método:** POST
- **URL:** `{{base_url}}/api/appointments/appointment-statuses/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "name": "En Proceso",
    "description": "Cita en proceso de atención",
    "is_active": true
  }
  ```

**Filtrar Estados Activos:**
- **Método:** GET
- **URL:** `{{base_url}}/api/appointments/appointment-statuses/?is_active=true`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`

**Actualizar Estado de Cita:**
- **Método:** PUT
- **URL:** `{{base_url}}/api/appointments/appointment-statuses/1/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "name": "Pendiente - Actualizado",
    "description": "Cita programada pero no confirmada. Estado actualizado con nueva información.",
    "is_active": true
  }
  ```

**Respuesta Exitosa:**
```json
{
  "id": 1,
  "name": "Pendiente - Actualizado",
  "description": "Cita programada pero no confirmada. Estado actualizado con nueva información.",
  "is_active": true,
  "created_at": "2025-08-21T10:00:00Z",
  "updated_at": "2025-08-21T19:30:00Z"
}
```

**Posibles Errores de Actualización:**
```json
{
  "name": [
    "Este campo es requerido."
  ]
}
```
```json
{
  "name": [
    "Ya existe un estado con este nombre."
  ]
}
```
```json
{
  "description": [
    "La descripción no puede estar vacía."
  ]
}
```

**Activar Estado:**
- **Método:** POST
- **URL:** `{{base_url}}/api/appointments/appointment-statuses/5/activate/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {}
  ```

**Respuesta Exitosa:**
```json
{
  "id": 5,
  "name": "En Proceso",
  "description": "Cita en proceso de atención",
  "is_active": true,
  "created_at": "2025-08-21T10:00:00Z",
  "updated_at": "2025-08-21T19:30:00Z"
}
```

**Posibles Errores:**
```json
{
  "detail": "El estado ya está activo."
}
```
```json
{
  "detail": "Estado no encontrado."
}
```

**Nota Importante sobre Activación:**
- **Solo funciona** con estados que están inactivos (`is_active: false`)
- **No requiere datos** en el body, solo el ID en la URL
- **Cambia `is_active`** de `false` a `true`
- **Mantiene** todos los datos originales del estado

### Citas
| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| **GET** | `/api/appointments/appointments/` | Listar citas | Requerida |
| **POST** | `/api/appointments/appointments/` | Crear cita | Requerida |
| **GET** | `/api/appointments/appointments/{id}/` | Ver cita específica | Requerida |
| **PUT** | `/api/appointments/appointments/{id}/` | Actualizar cita | Requerida |
| **DELETE** | `/api/appointments/appointments/{id}/` | Eliminar cita | Requerida |
| **GET** | `/api/appointments/appointments/completed/` | Citas completadas | Requerida |
| **GET** | `/api/appointments/appointments/pending/` | Citas pendientes | Requerida |
| **GET** | `/api/appointments/appointments/by_date_range/` | Citas por rango de fechas | Requerida |

#### Ejemplos de Citas

**Crear Cita:**
- **Método:** POST
- **URL:** `{{base_url}}/api/appointments/appointments/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "patient": 1,
    "therapist": 1,
    "appointment_date": "2025-08-25",
    "appointment_hour": "14:30:00",
    "appointment_status": 3,
    "appointment_type": "Fisioterapia",
    "room": "Sala 1",
    "ailments": "Dolor lumbar",
    "diagnosis": "Lumbalgia",
    "observation": "Paciente con dolor crónico"
  }
  ```

**Respuesta Exitosa:**
```json
{
  "id": 1,
  "patient": {
    "id": 1,
    "first_name": "María",
    "last_name": "González"
  },
  "therapist": {
    "id": 1,
    "first_name": "Ana",
    "last_name_paternal": "García"
  },
  "appointment_date": "2025-08-25",
  "appointment_hour": "14:30:00",
  "appointment_status": {
    "id": 1,
    "name": "Pendiente"
  },
  "appointment_type": "Fisioterapia",
  "room": "Sala 1",
  "ailments": "Dolor lumbar",
  "diagnosis": "Lumbalgia",
  "observation": "Paciente con dolor crónico",
  "is_active": true,
  "created_at": "2025-08-21T17:00:00Z"
}
```

**Ejemplos Adicionales de Citas:**

**Ejemplo 2:**
```json
{
  "patient": 2,
  "therapist": 1,
  "appointment_date": "2025-08-26",
  "appointment_hour": "10:00:00",
  "appointment_status": 4,
  "appointment_type": "Terapia Física",
  "room": "Sala 2",
  "ailments": "Lesión de rodilla",
  "diagnosis": "Esguince grado 1",
  "observation": "Paciente con dolor al caminar"
}
```

**Ejemplo 3:**
```json
{
  "patient": 3,
  "therapist": 2,
  "appointment_date": "2025-08-27",
  "appointment_hour": "16:00:00",
  "appointment_status": 5,
  "appointment_type": "Rehabilitación",
  "room": "Sala 3",
  "ailments": "Dolor de hombro",
  "diagnosis": "Tendinitis",
  "observation": "Paciente con limitación de movimiento"
}
```

**Posibles Errores de Validación:**
```json
{
  "patient": [
    "This field is required."
  ],
  "therapist": [
    "This field is required."
  ]
}
```

**Nota Importante sobre Estados de Cita:**
Los IDs de estados de cita disponibles en tu base de datos son:
- **ID: 2** - Confirmada (Activo: False)
- **ID: 3** - Completada (Activo: True) 
- **ID: 4** - En espera (Activo: True)
- **ID: 5** - En Proceso (Activo: True)

**❌ NO existe un estado con ID: 1**
```json
{
  "appointment_date": [
    "La fecha de la cita no puede ser en el pasado."
  ]
}
```
```json
{
  "appointment_hour": [
    "La hora de la cita no es válida."
  ]
}
```
```json
{
  "patient": [
    "El paciente seleccionado no existe."
  ]
}
```
```json
{
  "therapist": [
    "El terapeuta seleccionado no existe."
  ]
}
```

**Actualizar Cita Específica:**
- **Método:** PUT
- **URL:** `{{base_url}}/api/appointments/appointments/1/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "patient": 1,
    "therapist": 1,
    "appointment_date": "2025-08-26",
    "appointment_hour": "15:00:00",
    "appointment_status": 4,
    "appointment_type": "Fisioterapia - Actualizada",
    "room": "Sala 2",
    "ailments": "Dolor lumbar crónico",
    "diagnosis": "Lumbalgia aguda",
    "observation": "Paciente con dolor crónico. Se actualizó el tipo de cita y la sala."
  }
  ```

**Respuesta Exitosa:**
```json
{
  "id": 1,
  "patient": {
    "id": 1,
    "first_name": "María",
    "last_name": "González"
  },
  "therapist": {
    "id": 1,
    "first_name": "Ana",
    "last_name_paternal": "García"
  },
  "appointment_date": "2025-08-26",
  "appointment_hour": "15:00:00",
  "appointment_status": {
    "id": 4,
    "name": "En espera"
  },
  "appointment_type": "Fisioterapia - Actualizada",
  "room": "Sala 2",
  "ailments": "Dolor lumbar crónico",
  "diagnosis": "Lumbalgia aguda",
  "observation": "Paciente con dolor crónico. Se actualizó el tipo de cita y la sala.",
  "is_active": true,
  "created_at": "2025-08-21T17:00:00Z",
  "updated_at": "2025-08-21T19:30:00Z"
}
```

**Posibles Errores de Actualización:**
```json
{
  "patient": [
    "El paciente seleccionado no existe."
  ]
}
```
```json
{
  "therapist": [
    "El terapeuta seleccionado no existe."
  ]
}
```
```json
{
  "appointment_status": [
    "Invalid pk \"1\" - object does not exist."
  ]
}
```
```json
{
  "appointment_date": [
    "La fecha de la cita no puede ser en el pasado."
  ]
}
```

**Filtrar Citas por Fecha:**
- **Método:** GET
- **URL:** `{{base_url}}/api/appointments/appointments/?appointment_date=2025-08-25`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`

**Obtener Citas Completadas:**
- **Método:** GET
- **URL:** `{{base_url}}/api/appointments/appointments/completed/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`

**Citas por Rango de Fechas:**
- **Método:** GET
- **URL:** `{{base_url}}/api/appointments/appointments/by_date_range/?start_date=2025-08-20&end_date=2025-08-30`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`

**Respuesta Exitosa:**
```json
[
  {
    "id": 1,
    "patient": {
      "id": 1,
      "first_name": "María",
      "last_name": "González"
    },
    "therapist": {
      "id": 1,
      "first_name": "Ana",
      "last_name_paternal": "García"
    },
    "appointment_date": "2025-08-25",
    "appointment_hour": "14:30:00",
    "appointment_status": {
      "id": 3,
      "name": "Completada"
    },
    "appointment_type": "Fisioterapia",
    "room": "Sala 1",
    "ailments": "Dolor lumbar",
    "diagnosis": "Lumbalgia",
    "observation": "Paciente con dolor crónico",
    "is_active": true,
    "created_at": "2025-08-21T17:00:00Z"
  }
]
```

**Posibles Errores:**
```json
{
  "error": "Se requieren start_date y end_date"
}
```
```json
{
  "error": "El formato de fecha debe ser YYYY-MM-DD"
}
```
```json
{
  "error": "start_date no puede ser mayor que end_date"
}
```

**Nota Importante sobre Rango de Fechas:**
- **Parámetros obligatorios**: `start_date` y `end_date` en la URL
- **Formato de fecha**: YYYY-MM-DD (ejemplo: 2025-08-20)
- **Ejemplos de uso**:
  - Rango de una semana: `?start_date=2025-08-20&end_date=2025-08-27`
  - Rango de un mes: `?start_date=2025-08-01&end_date=2025-08-31`
  - Rango de un día: `?start_date=2025-08-25&end_date=2025-08-25`
- **NO uses** `/api/appointments/appointments/by_date_range/` sin los parámetros

### Tickets
| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| **GET** | `/api/appointments/tickets/` | Listar tickets | Requerida |
| **POST** | `/api/appointments/tickets/` | Crear ticket | Requerida |
| **GET** | `/api/appointments/tickets/{id}/` | Ver ticket específico | Requerida |
| **PUT** | `/api/appointments/tickets/{id}/` | Actualizar ticket | Requerida |
| **DELETE** | `/api/appointments/tickets/{id}/` | Eliminar ticket | Requerida |
| **GET** | `/api/appointments/tickets/paid/` | Tickets pagados | Requerida |
| **GET** | `/api/appointments/tickets/pending/` | Tickets pendientes | Requerida |
| **GET** | `/api/appointments/tickets/cancelled/` | Tickets cancelados | Requerida |
| **POST** | `/api/appointments/tickets/{id}/mark_as_paid/` | Marcar como pagado | Requerida |
| **POST** | `/api/appointments/tickets/{id}/mark_as_cancelled/` | Marcar como cancelado | Requerida |

#### Ejemplos de Tickets

**Crear Ticket:**
- **Método:** POST
- **URL:** `{{base_url}}/api/appointments/tickets/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "appointment": 3,
    "ticket_number": "TKT-001",
    "amount": 150.00,
    "payment_method": "Efectivo",
    "description": "Sesión de fisioterapia",
    "status": "pending"
  }
  ```

**Respuesta Exitosa:**
```json
{
  "id": 1,
  "appointment": {
    "id": 3,
    "appointment_date": "2025-08-25"
  },
  "ticket_number": "TKT-001",
  "amount": "150.00",
  "payment_method": "Efectivo",
  "description": "Sesión de fisioterapia",
  "status": "pending",
  "payment_date": null,
  "is_active": true,
  "created_at": "2025-08-21T17:30:00Z"
}
```

**Ejemplos Adicionales de Tickets:**

**Ejemplo 2:**
```json
{
  "appointment": 2,
  "ticket_number": "TKT-002",
  "amount": 200.00,
  "payment_method": "Tarjeta",
  "description": "Terapia física para lesión de rodilla",
  "status": "paid"
}
```

**Ejemplo 3:**
```json
{
  "appointment": 3,
  "ticket_number": "TKT-003",
  "amount": 180.00,
  "payment_method": "Transferencia",
  "description": "Rehabilitación para dolor de hombro",
  "status": "pending"
}
```

**📋 Ejemplo Completo - Crear Cita y Ticket:**

**Paso 1: Crear Cita**
```json
POST {{base_url}}/api/appointments/appointments/
{
  "patient": 1,
  "therapist": 1,
  "appointment_date": "2025-08-25",
  "appointment_hour": "14:30:00",
  "appointment_status": 3,
  "appointment_type": "Fisioterapia",
  "room": "Sala 1",
  "ailments": "Dolor lumbar",
  "diagnosis": "Lumbalgia",
  "observation": "Paciente con dolor crónico"
}
```

**Respuesta de Cita Creada:**
```json
{
  "id": 1,
  "patient": {
    "id": 1,
    "first_name": "María",
    "last_name": "González"
  },
  "therapist": {
    "id": 1,
    "first_name": "Ana",
    "last_name_paternal": "García"
  },
  "appointment_date": "2025-08-25",
  "appointment_hour": "14:30:00",
  "appointment_status": {
    "id": 3,
    "name": "Completada"
  },
  "appointment_type": "Fisioterapia",
  "room": "Sala 1",
  "ailments": "Dolor lumbar",
  "diagnosis": "Lumbalgia",
  "observation": "Paciente con dolor crónico",
  "is_active": true,
  "created_at": "2025-08-21T17:00:00Z"
}
```

**Paso 2: Crear Ticket (usando ID de cita = 3)**
```json
POST {{base_url}}/api/appointments/tickets/
{
  "appointment": 3,
  "ticket_number": "TKT-001",
  "amount": 150.00,
  "payment_method": "Efectivo",
  "description": "Sesión de fisioterapia",
  "status": "pending"
}
```

**Posibles Errores de Validación:**
```json
{
  "appointment": [
    "This field is required."
  ]
}
```
```json
{
  "ticket_number": [
    "Este campo es requerido."
  ],
  "amount": [
    "Este campo es requerido."
  ]
}
```
```json
{
  "appointment": [
    "Invalid pk \"999\" - object does not exist."
  ]
}
```
```json
{
  "ticket_number": [
    "Ya existe un ticket con este número."
  ]
}
```
```json
{
  "amount": [
    "El monto debe ser mayor a 0."
  ]
}
```
```json
{
  "payment_method": [
    "Método de pago no válido."
  ]
}
```
```json
{
  "status": [
    "Estado no válido. Opciones: pending, paid, cancelled"
  ]
}
```

**Nota Importante sobre Tickets:**
- **`appointment`**: ID de la cita (no `appointment_id`)
- **`ticket_number`**: Número único del ticket
- **`amount`**: Monto en decimal (ejemplo: 150.00)
- **`payment_method`**: Método de pago (Efectivo, Tarjeta, Transferencia, etc.)
- **`status`**: Estado del ticket (pending, paid, cancelled)
- **`description`**: Descripción opcional del servicio

**⚠️ IMPORTANTE - Crear Cita Primero:**
Antes de crear un ticket, **DEBES crear una cita primero**. Los IDs disponibles son:
- **Pacientes**: ID 1, 2, 3, 4
- **Terapeutas**: ID 1, 2
- **Estados de cita**: ID 2, 3, 4, 5

**Cita existente en tu base de datos:**
- **ID: 3** - María Elena González López (Fecha: 2025-08-25, Estado: Completada)

**Pasos para crear un ticket:**
1. **Crear cita**: POST `/api/appointments/appointments/` con datos válidos
2. **Obtener ID de cita**: De la respuesta de la cita creada
3. **Crear ticket**: POST `/api/appointments/tickets/` usando el ID de cita obtenido

**Para usar la cita existente:**
Usa `"appointment": 3` en lugar de `"appointment": 1`

**Marcar Ticket como Pagado:**
- **Método:** POST
- **URL:** `{{base_url}}/api/appointments/tickets/1/mark_as_paid/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {}
  ```

**Respuesta Exitosa:**
```json
{
  "id": 1,
  "appointment": {
    "id": 3,
    "appointment_date": "2025-08-25"
  },
  "ticket_number": "TKT-001",
  "amount": "150.00",
  "payment_method": "Efectivo",
  "description": "Sesión de fisioterapia",
  "status": "paid",
  "payment_date": "2025-08-21T20:00:00Z",
  "is_active": true,
  "created_at": "2025-08-21T17:30:00Z",
  "updated_at": "2025-08-21T20:00:00Z"
}
```

**Posibles Errores:**
```json
{
  "detail": "No Ticket matches the given query."
}
```
```json
{
  "detail": "El ticket ya está pagado."
}
```
```json
{
  "detail": "No se puede marcar como pagado un ticket cancelado."
}
```

**Nota Importante sobre Marcar como Pagado:**
- **Solo funciona** con tickets que están en estado `pending`
- **No requiere datos** en el body, solo el ID en la URL
- **Cambia `status`** de `pending` a `paid`
- **Actualiza `payment_date`** automáticamente con la fecha y hora actual
- **Mantiene** todos los demás datos del ticket

**⚠️ IMPORTANTE - Crear Ticket Primero:**
Antes de marcar un ticket como pagado, **DEBES crear un ticket primero**. Los pasos son:
1. **Crear cita**: POST `/api/appointments/appointments/` con datos válidos
2. **Crear ticket**: POST `/api/appointments/tickets/` usando el ID de cita obtenido
3. **Marcar como pagado**: POST `/api/appointments/tickets/{id}/mark_as_paid/` usando el ID del ticket creado

**Para usar la cita existente:**
Usa `"appointment": 3` en el ticket (ID de la cita existente)

**Actualizar Ticket Específico:**
- **Método:** PUT
- **URL:** `{{base_url}}/api/appointments/tickets/1/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "appointment": 3,
    "ticket_number": "TKT-001-ACTUALIZADO",
    "amount": 180.00,
    "payment_method": "Tarjeta",
    "description": "Sesión de fisioterapia - Actualizada con nueva información",
    "status": "paid"
  }
  ```

**Respuesta Exitosa:**
```json
{
  "id": 1,
  "appointment": {
    "id": 3,
    "appointment_date": "2025-08-25"
  },
  "ticket_number": "TKT-001-ACTUALIZADO",
  "amount": "180.00",
  "payment_method": "Tarjeta",
  "description": "Sesión de fisioterapia - Actualizada con nueva información",
  "status": "paid",
  "payment_date": "2025-08-21T20:00:00Z",
  "is_active": true,
  "created_at": "2025-08-21T17:30:00Z",
  "updated_at": "2025-08-21T20:00:00Z"
}
```

**Posibles Errores de Actualización:**
```json
{
  "appointment": [
    "Invalid pk \"999\" - object does not exist."
  ]
}
```
```json
{
  "ticket_number": [
    "Ya existe un ticket con este número."
  ]
}
```
```json
{
  "amount": [
    "El monto debe ser mayor a 0."
  ]
}
```
```json
{
  "payment_method": [
    "Método de pago no válido."
  ]
}
```
```json
{
  "status": [
    "Estado no válido. Opciones: pending, paid, cancelled"
  ]
}
```

**Nota Importante sobre Actualización de Tickets:**
- **`appointment`**: ID de la cita (debe existir)
- **`ticket_number`**: Número único del ticket (no puede duplicarse)
- **`amount`**: Monto en decimal (debe ser mayor a 0)
- **`payment_method`**: Método de pago válido
- **`status`**: Estado válido (pending, paid, cancelled)
- **`description`**: Descripción opcional del servicio
- **`payment_date`**: Se actualiza automáticamente cuando el status cambia a "paid"

**Filtrar Tickets por Estado:**
- **Método:** GET
- **URL:** `{{base_url}}/api/appointments/tickets/?status=pending`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`

---

## ⚙️ Módulo 6: Historiales y Configuraciones (`/api/configurations/`)

### Historiales
| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| **GET** | `/api/configurations/histories/` | Listar historiales | Requerida |
| **POST** | `/api/configurations/histories/create/` | Crear historial | Requerida |
| **POST** | `/api/configurations/histories/{id}/delete/` | Eliminar historial | Requerida |

#### Ejemplos de Historiales

**Crear Historial:**
- **Método:** POST
- **URL:** `{{base_url}}/api/configurations/histories/create/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {
    "document_type": 1,
    "document_number": "12345678"
  }
  ```

**Respuesta Exitosa:**
```json
{
  "id": 1
}
```

**Ejemplos Adicionales de Historiales:**

**Ejemplo 2:**
```json
{
  "document_type": 1,
  "document_number": "87654321"
}
```

**Ejemplo 3:**
```json
{
  "document_type": 1,
  "document_number": "11111111"
}
```

**Ejemplo 4:**
```json
{
  "document_type": 1,
  "document_number": "99999999"
}
```

**Ejemplo 5:**
```json
{
  "document_type": 1,
  "document_number": "55555555"
}
```

**Posibles Errores de Validación:**
```json
{
  "error": "Campos obligatorios faltantes"
}
```
```json
{
  "error": "JSON inválido"
}
```
```json
{
  "error": "document_type inválido"
}
```
```json
{
  "error": "Ya existe un historial activo con este tipo de documento y número",
  "existing_history_id": 1
}
```

**Nota Importante sobre Historiales:**
- **`document_type`**: ID del tipo de documento (debe existir)
- **`document_number`**: Número del documento (obligatorio)

**⚠️ IMPORTANTE - Tipos de Documento Disponibles:**
- **ID: 1** - DNI (Documento Nacional de Identidad)

**Nota sobre el Modelo History:**
Este endpoint crea un historial básico con solo tipo de documento y número. Los campos adicionales como `testimony`, `observation`, `height`, `weight`, etc. se pueden actualizar posteriormente si es necesario.

**⚠️ RESTRICCIÓN ÚNICA IMPORTANTE:**
- No puede existir más de un historial activo con la misma combinación de `document_type` y `document_number`
- Si intentas crear un historial con una combinación que ya existe, recibirás un error 409 (Conflict)
- Para reutilizar una combinación, primero debes eliminar (soft delete) el historial existente

**Eliminar Historial:**
- **Método:** POST
- **URL:** `{{base_url}}/api/configurations/histories/2/delete/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (raw JSON):**
  ```json
  {}
  ```

**Respuesta Exitosa:**
```json
{
  "status": "deleted"
}
```

**Posibles Errores:**
```json
{
  "error": "No encontrado"
}
```

**Nota Importante sobre Eliminación:**
- **Método POST**: Aunque es una eliminación, usa POST, no DELETE
- **Soft Delete**: Marca el historial como eliminado (`deleted_at = now()`) pero no lo borra físicamente
- **Body vacío**: No requiere datos en el body, solo el ID en la URL
- **Reutilización**: Después de eliminar, puedes crear un nuevo historial con la misma combinación de documento

---

## 🔐 Autenticación

### Credenciales de Prueba
```
Username: xxangelx31@gmail.com
Password: edu123
```

### Métodos de Autenticación
1. **Basic Auth** (Recomendado para pruebas)
   - En Postman: Authorization tab → Basic Auth
   - Username: `xxangelx31@gmail.com`
   - Password: `edu123`
   
2. **Session Auth** (Para navegador)
   - Login en: `http://localhost:8000/admin/`

### Configuración en Postman
1. **Authorization tab** → **Basic Auth**
2. **Username:** `xxangelx31@gmail.com`
3. **Password:** `edu123`
4. **URL:** `{{base_url}}/api/appointments/appointment-statuses/`

---

## 📊 Ejemplos de Respuestas

### Estado de Cita
```json
{
  "id": 3,
  "name": "Completada",
  "description": "Cita completada exitosamente",
  "is_active": true,
  "created_at": "2025-08-21T20:22:27.178462Z",
  "updated_at": "2025-08-21T20:22:27.178462Z"
}
```

### Lista Paginada
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 3,
      "name": "Completada",
      "description": "Cita completada",
      "is_active": true
    }
  ]
}
```

### Error de Autenticación
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### Error de Validación
```json
{
  "name": [
    "Este campo es requerido."
  ],
  "email": [
    "Ingrese una dirección de correo válida."
  ]
}
```

---
## ⚙️ Módulo 8: Empresa y reportes (`/api/company/`)
### Empresa
|   Método   | Endpoint | Descripción | Autenticación |
|------------|----------|-------------|---------------|
| **GET**    |  `/api/company/company/` | Listar Empresa | Requerida |
| **POST**   |  `/api/company/company/` | Crear Empresa  | Requerida |
| **GET**    | `/api/company/company/{id}/` | Ver empresa específica | Requerida |
| **POST**   | `/api/company/company/{id}/upload_logo/` | Subir Logo | Requerida |
| **DELETE** | `/api/company/company/{id}` | Eliminar Empresa | Requerida |
| **DELETE** | `/api/company/company/{id}/delete_logo/` | Eliminar Logo | Requerida |
| **GET**    | `/api/company/company/{id}/show_logo/` | Mostrar Logo | Requerida |
| **PUT**    | `/api/company/company/{id}/` | Actualizar Nombre y Logo | Requerida |

### Ejemplo de Empresa
**Crear Empresa**
**Método**:POST
**URL**: `{{base_url}}/api/company/company/`
-**Auth**: Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
-**Headers:**
-**Body (raw):**
```json
{
  "company_name": "Reflexo"
}
```

**Respuesta Exitosa:**
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

**Ejemplos Adicionales de Empresa:**

**Ejemplo 2:**
```json
{
  "company_name": "Reflexo2"
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

**Nota Importante sobre crear  la empresa**
Al crear una empresa no se tiene que poner el mismo nombre , la idea esa solo usar la unica empresa creada y editarla aunque
se pueda crear más.

------------------------------------------------------------------------------

**Subir Logo**
- **Método:** POST
- **URL:** `{{base_url}}/api/company/company/{id}/upload_logo/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/json
  ```
- **Body (Form-data):**
  |        Key         |       Value        | 
  |--------------------|--------------------|
  | logo       [file]  |  *escoger imagen*  | 
  |-----------------------------------------|

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
**Nota Importante sobre crear  la empresa**
-*Colocar en la parte de key "logo" y seleccionar file, por defecto está text*
-*No subir una imagen de mas de 2mb*
-*Solo se puede subir un logo si la empresa no cuenta con ella, para actualizar se usa put*

-------------------------------------------------------------------------------------------

**Eliminar Empresa**
**Método**:DELETE
**URL**: `{{base_url}}/api/company/company/{id}`
-**Auth**: Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
-**Headers:**
-**Body (raw):**

**Respuesta Exitosa:**
```json
{
    "status": "success",
    "message": "Empresa \"REFLEXO1\" eliminada correctamente"
}
```
**Posibles Errores al Elimnar empresa**

```json
{
    "status": "error",
    "message": "Empresa no encontrada"
}
```
**Nota Importante sobre eliminar empresa**
-*Colocar el id correcto de la empresa creada*

**Eliminar Logo**
**Método**:DELETE
**URL**: `{{base_url}}/api/company/company/{id}/delete_logo`
-**Auth**: Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
-**Headers:**
-**Body (raw):**

**Respuesta Exitosa:**
```json
{
    "message": "Logo eliminado correctamente"
}
```
**Posibles Errores Logo**

```json
{
    "detail": "No CompanyData matches the given query."
}
```
**Nota Importante sobre eliminar empresa**
-*Colocar el id correcto de la empresa creada*

--------------------------------------------------------------

**Actualizar Empresa**
*SOLO ACTUALIZAR EL NOMBRE*
- **Método:** PUT
- **URL:** `{{base_url}}/api/company/company/{id}/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
-**Body (raw):** 

```json
{
  "company_name": "empresaT"
}
```

**Respuesta Exitosa:**
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
*ACTUALIZAR NOMBRE Y LOGO*
- **Método:** PUT
- **URL:** `{{base_url}}/api/company/company/{id}/`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
- **Body (Form-data):**
  |        Key           |       Value        | 
  |----------------------|--------------------|
  | company_name  [text] |       reflexo      | 
  |----------------------|--------------------|
  | company_logo  [file] |  *escoger imagen*  |
  |----------------------|--------------------|

**Respuesta Exitosa:**
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
**Advertencias**
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

```json
{
    "warning": "El logo no se actualizó: El logo excede el tamaño máximo permitido de 2097152 bytes.",
    "id": 1,
    "company_name": "reflexo",
    "company_logo": "reflexo.jpg",
    "logo_url": "http://127.0.0.1:8000/media/logos/oskar-smethurst-B1GtwanCbiw-unsplash_1.jpg",
    "has_logo": true,
    "created_at": "2025-08-24T16:24:25.239714Z",
    "updated_at": "2025-08-24T17:16:38.328992Z"
}
```
**Nota Importante Actualizar Empresa**
-*Hay dos maneras de actualizar una por "raw" solo actualiza el nombre y la otra manera "Form-data" permite ambos el nombre y el logo*
-*La imagen se actualiza solo si es un formtato de imagen permitido o si no pasa los 2mb de lo contrario te da una advertencia y se queda la imagen que ya tenia antes*
-**si pones PATCH en vez de PUT realiza lo mismo**

### Reportes
### Cuando generen la cita pongan payment, payment_type, ,payment_type_name para que se muestre bien los reports:
| Método     | Endpoint                                                                                     | Descripción               | Autenticación |
|--------    |----------------------------------------------------------------------------------------------|-------------              |---------------|
| **GET**    | `/api/company/reports/appointments-per-therapist/?date=2025-08-25`                           | Reporte por terapeuta     | Requerida     |
| **GET**    | `/api/company/reports/daily-cash/?date=2025-08-25`                                           | Caja diaria               | Requerida     |
| **GET**    | `/api/company/reports/patients-by-therapist/?date=2025-08-25`                                | Pacientes por terapeuta   | Requerida     |
| **GET**    | `/api/company/reports/appointments-between-dates/?start_date=2025-08-25&end_date=2025-08-28` | Citas entre fechas        | Requerida     |
| **GET**    | `/api/company/exports/excel/citas-rango/?start_date=2025-08-25&end_date=2025-08-28`          | Generar reporte en excel  | Requerida     |


### Ejemplos de reporte de citas por terapeuta
**Mostrar: "Reporte de cita por terapeuta":**
- **Método: GET** 
- **URL:** `{{base_url}}/api/company/reports/appointments-per-therapist/?date=2025-08-25`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/JSON
  ```
**Respuesta Exitosa:**
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


### Ejemplos de Reporte diario de caja
**Mostrar: "Reporte de diario de caja":**
- **Método: GET** 
- **URL:** `{{base_url}}/api/company/reports/daily-cash/?date=2025-08-25`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/JSON
  ```
**Respuesta Exitosa:**
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

### Ejemplos de Reporte de pacientes por Terapeuta
**Mostrar: "Reporte de paciente por Terapeuta":**
- **Método: GET** 
- **URL:** `{{base_url}}/api/company/reports/patients-by-therapist/?date=2025-08-25`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`
- **Headers:**
  ```
  Content-Type: application/JSON
  ```
**Respuesta Exitosa:**
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


### Ejemplos de Reporte de Citas en un rango de fechas
**Mostrar: "Reporte citas entre fechas":**
- **Método: GET** 
- **URL:** `{{base_url}}/api/company/reports/appointments-between-dates/?start_date=2025-08-25&end_date=2025-08-28`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`

**Respuesta Exitosa:**

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
    },
    {
        "appointment_id": 3,
        "patient_id": 1,
        "document_number_patient": "11111111",
        "patient": "García Hernández Ana Sofía",
        "primary_phone_patient": "+51 444 444 444",
        "appointment_date": "2025-08-25",
        "appointment_hour": "14:30"
    }
]
```

**Nota Importante sobre Reporte de pacientes por Terapeuta:**
- **Debe contener lo necesario**: De haber un paciente, una fecha exacta de la cita y también una hora de la cita .
--------------------------------------------------------------

**Mostrar: "Reporte citas entre fechas (EXCEL)":**
- **Método: GET** 
- **URL:** `{{base_url}}/api/company/reports/patients-by-therapist/?date=2025-08-25`
- **Auth:** 
- **Headers:**

**Probarlo en un navegador**
**Respuesta Exitosa:**
*se genera un excel*

ID Paciente	DNI/Documento	Paciente	      Teléfono	      Fecha	   Hora
1	11111111	García Hernández Ana Sofía	+51 444 444 444	2025-08-25	14:30
1	11111111	García Hernández Ana Sofía	+51 444 444 444	2025-08-25	14:30
1	11111111	García Hernández Ana Sofía	+51 444 444 444	2025-08-25	14:30
1	11111111	García Hernández Ana Sofía	+51 444 444 444	2025-08-25	14:30
1	11111111	García Hernández Ana Sofía	+51 444 444 444	2025-08-25	14:30

**Nota Importante**
-**Usar el endpoint en un navegador ya que si se pone en el postman no se ve de una manera adecuado**


------------------------------------------------------------------------------------------------------------------------

### Estadísticas
| Método     | Endpoint                                                               | Descripción                    | Autenticación |
|--------    |----------------------------------------------------------------------- |--------------------------------|---------------|
| **GET**    | `/api/company/reports/statistics/?start=2025-08-25&end=2025-08-28`     | Mostrar estadísticas de datos  | Requerida     |


### Ejemplos de Estadísticas
**Mostrar: "Estadísticas de datos":**
- **Método: GET** 
- **URL:** `{{base_url}}/api/company/reports/statistics/?start=2025-08-25&end=2025-08-28`
- **Auth:** Basic Auth
  - Username: `xxangelx31@gmail.com`
  - Password: `edu123`

**Respuesta Exitosa:**
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
**Nota Importante sobre Reporte de pacientes por Terapeuta:**
- **Debe existir lo necesario**: Se debe haber ingresado datos como ingresos, citas, cant. de tipo de pacientes, terapeutas, etc.

--------------------------------------------------------------------------------------------

## 🔍 Filtros y Búsquedas

### Filtros Comunes
- `is_active=true/false` - Filtrar por estado activo
- `search=texto` - Búsqueda por texto
- `ordering=field` - Ordenar por campo

### Ejemplos de Filtros
```
GET /api/appointments/appointment-statuses/?is_active=true
GET /api/therapists/therapists/?search=ana
GET /api/patients/patients/?ordering=-created_at
GET /api/appointments/appointments/?appointment_date=2025-08-25
GET /api/therapists/therapists/?region=1&active=true
```

### Combinación de Filtros
```
GET /api/therapists/therapists/?region=1&active=true&search=ana
```

---

## 📝 Notas Importantes

1. **Autenticación**: La mayoría de endpoints requieren autenticación
2. **Paginación**: Los endpoints de listado incluyen paginación automática
3. **Soft Delete**: Algunos recursos usan eliminación lógica
4. **Filtros**: Se pueden combinar múltiples filtros
5. **Búsqueda**: La búsqueda es case-insensitive
6. **Fechas**: Usar formato ISO 8601 (YYYY-MM-DD)
7. **Horas**: Usar formato 24h (HH:MM:SS)

---

## 🚀 Uso en Desarrollo

### Iniciar Servidor
```bash
python manage.py runserver
```

### Configuración en Postman
1. **Importar colección**: `Backend_Reflexo_MTV_API.postman_collection.json`
2. **Variables de entorno**:
   - `base_url`: `http://localhost:8000`
3. **Autenticación automática** configurada en todos los endpoints

### Documentación Interactiva
- **Admin Django**: `http://localhost:8000/admin/`
- **Browsable API**: Disponible en todos los endpoints GET

### Herramientas Recomendadas
- **Postman**: Para pruebas de API
- **Insomnia**: Alternativa a Postman
- **Thunder Client**: Extensión de VS Code
- **httpie**: Para línea de comandos (alternativa a curl)

