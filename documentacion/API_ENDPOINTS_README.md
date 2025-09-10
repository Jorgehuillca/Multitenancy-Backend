# API Endpoints (Postman-Ready)

Base URL: http://localhost:8000/api

Authentication: Most endpoints expect JWT or Session auth if enforced by the view permissions. Unless noted as `AllowAny`, send `Authorization: Bearer <token>` header.

Notes
- Pagination and filtering follow DRF conventions unless otherwise specified.
- For ViewSets registered with routers, detail endpoints use `/<resource>/{id}/`.
- Date formats are ISO-8601 unless noted.

---

## Architect Module
Base: http://localhost:8000/api/architect/

- auth
  - POST http://localhost:8000/api/architect/auth/login/
    
    Body (JSON):
    ```json
    {
      "email": "admin@gmail.com",
      "password": "admin123456"
    }
    ```
    
    Alternativas (otros usuarios):
    ```json
    { "email": "senati@gmail.com", "password": "wilber123456" }
    ```
    ```json
    { "email": "prueba2@gmail.com", "password": "clinica23456" }
    ```

  - POST http://localhost:8000/api/architect/auth/register/
    
    Body (JSON):
    ```json
    {
      "email": "new@example.com",
      "user_name": "newuser",
      "document_number": "12345678",
      "name": "Nombre",
      "paternal_lastname": "ApellidoP",
      "maternal_lastname": "ApellidoM",
      "password": "NewPass#123",
      "password_confirm": "NewPass#123"
    }
    ```
- users
  - GET http://localhost:8000/api/architect/users/
  - POST http://localhost:8000/api/architect/users/
    
    Body (JSON):
    ```json
    {
      "email": "u@example.com",
      "user_name": "userexample",
      "document_number": "87654321",
      "name": "User",
      "paternal_lastname": "Example",
      "maternal_lastname": "Demo",
      "password": "NewPass#123"
    }
    ```
- permissions
  - GET http://localhost:8000/api/architect/permissions/
- roles
  - GET http://localhost:8000/api/architect/roles/

---

## Users Profiles Module
Base: http://localhost:8000/api/profiles/

- users (current user)
  - GET http://localhost:8000/api/profiles/users/me/
  - PUT/PATCH http://localhost:8000/api/profiles/users/me/update/
  - POST http://localhost:8000/api/profiles/users/me/photo/
    
    Opción A (JSON):
    Body (JSON):
    ```json
    {
      "photo_url": "/media/users/photos/profile.jpg"
    }
    ```
    Opción B (multipart/form-data):
    Body (form-data):
    - Key: `photo_file` | Type: File | Value: seleccionar imagen
  - DELETE http://localhost:8000/api/profiles/users/me/photo/
  - GET http://localhost:8000/api/profiles/users/search/?q=test&page=1
    (Parámetros: q=texto_búsqueda, page=número_página)
  - GET http://localhost:8000/api/profiles/users/profile/

- profiles
  - GET http://localhost:8000/api/profiles/profiles/me/
  - POST http://localhost:8000/api/profiles/profiles/create/
    
    Body (JSON):
    ```json
    {
      "name": "Nuevo Usuario",
      "paternal_lastname": "ApellidoP",
      "maternal_lastname": "ApellidoM", 
      "email": "nuevo@example.com",
      "document_number": "87654324",
      "phone": "999999999",
      "sex": "M"
    }
    ```
    
    **NOTA:** Este endpoint NO crea usuarios nuevos. Actualiza/completa el perfil del usuario autenticado (el del token con el que haces la solicitud). Si deseas crear un usuario nuevo, usa el endpoint de registro:
    - `POST /api/architect/auth/register/` con los campos: `email`, `user_name`, `document_number`, `name`, `paternal_lastname`, `maternal_lastname`, `password`, `password_confirm`.
  - GET http://localhost:8000/api/profiles/profiles/public/{user_name}/
    
    Nota:
    - Este endpoint busca por el campo `user_name` del usuario y solo devuelve perfiles con `is_active=True`.
    - Retorna 404 Not Found cuando:
      - No existe un usuario con ese `user_name`.
      - El usuario existe pero no está activo (`is_active=False`).
    - Asegúrate de pasar exactamente el `user_name` (no el email) en la URL.
  - PATCH http://localhost:8000/api/profiles/profiles/settings/
  - GET http://localhost:8000/api/profiles/profiles/completion/
  - GET http://localhost:8000/api/profiles/profiles/search/?q=test&page=1
    (Parámetros: q=texto_búsqueda, page=número_página)

- password
  - POST http://localhost:8000/api/profiles/password/change/
    
    Body (JSON):
    ```json
    {
      "current_password": "oldpass",
      "new_password": "NewPass#123",
      "new_password_confirm": "NewPass#123"
    }
    ```
    Nota: este endpoint cambia la contraseña del usuario autenticado (el dueño del token). `current_password` debe ser la contraseña actual de ese usuario.
  - POST http://localhost:8000/api/profiles/password/reset/
    
    Body (JSON):
    ```json
    {
      "email": "user@example.com"
    }
    ```
    Nota: no requiere autenticación (AllowAny). Envía un código de verificación para cambio de contraseña. El `email` debe pertenecer a un usuario existente; de lo contrario, responderá 400 con error de validación.
  - POST http://localhost:8000/api/profiles/password/reset/confirm/
    
    Body (JSON):
    ```json
    {
      "code": "123456",
      "new_password": "NewPass#123",
      "new_password_confirm": "NewPass#123"
    }
    ```
    Nota: no requiere autenticación (AllowAny). Usa el campo `code` (no `uid/token`).
  - POST http://localhost:8000/api/profiles/password/strength/
    
    Body (JSON):
    ```json
    {
      "password": "Candidate#123"
    }
    ```
    Nota: no requiere autenticación (AllowAny). Solo valida la fortaleza de la contraseña enviada.
  - GET http://localhost:8000/api/profiles/password/history/
  - GET http://localhost:8000/api/profiles/password/policy/

- verification
  - POST http://localhost:8000/api/profiles/verification/code/
    
    Body (JSON):
    ```json
    {
      "verification_type": "email_change",
      "target_email": "new@example.com"
    }
    ```
    Nota: requiere autenticación (IsAuthenticated).
    - `verification_type` es obligatorio. Valores soportados: `email_change` (y según configuración, `email_verification`).
    - Si `verification_type` = `email_change`, también debes enviar `target_email` válido y diferente al actual.
  - POST http://localhost:8000/api/profiles/verification/code/resend/
    
    Body (JSON):
    ```json
    {
      "verification_type": "email_change",
      "target_email": "new@example.com"
    }
    ```
    Nota: requiere autenticación (IsAuthenticated). Reenvía un nuevo código e invalida los anteriores para ese tipo.

  - POST http://localhost:8000/api/profiles/verification/email/
    
    Body (JSON):
    ```json
    {
      "email": "user@example.com"
    }
    ```
    Nota: no requiere autenticación (AllowAny). El `email` debe pertenecer a un usuario existente y no estar verificado; de lo contrario responderá 400.
  - POST http://localhost:8000/api/profiles/verification/email/confirm/
    
    Body (JSON):
    ```json
    {
      "code": "123456"
    }
    ```
  - POST http://localhost:8000/api/profiles/verification/email/change/
    
    Body (JSON):
    ```json
    {
      "new_email": "new@example.com"
    }
    ```
    Nota: requiere autenticación (IsAuthenticated). `new_email` debe ser un correo NO registrado en ningún usuario. Si el correo ya existe, responde 400 con el error "Este email ya está registrado". Si el correo no existe, responde 200 y envía un código de verificación (en desarrollo se devuelve en la respuesta) para confirmar el cambio con `/api/profiles/verification/email/confirm/`.
  - POST http://localhost:8000/api/profiles/verification/email/change/confirm/
    
    Body (JSON):
    ```json
    {
      "code": "123456"
    }
    ```
  - POST http://localhost:8000/api/profiles/verification/code/resend/
    
    Body (JSON):
    ```json
    {
      "verification_type": "email_change",
      "target_email": "new@example.com"
    }
    ```
    Nota: requiere autenticación (IsAuthenticated). Debes usar una cuenta de usuario registrada (el dueño del token). Si `verification_type` = `email_change`, envía también `target_email` válido y diferente al email actual.
  - GET http://localhost:8000/api/profiles/verification/status/


---

## Patients & Diagnoses Module
Base: http://localhost:8000/api/patients/

- diagnoses
  - GET http://localhost:8000/api/patients/diagnoses/
  - POST http://localhost:8000/api/patients/diagnoses/
    
    Body (JSON):
    ```json
    {
      "name": "Lumbalgia",
      "code": "DX001"
    }
    ```
  - GET http://localhost:8000/api/patients/diagnoses/{id}/
  - PUT http://localhost:8000/api/patients/diagnoses/{id}/
  - DELETE http://localhost:8000/api/patients/diagnoses/{id}/
  - GET http://localhost:8000/api/patients/diagnoses/search/?q={text}
    
    Nota:
    - El parámetro `q` puede ser cualquier texto (o número) para buscar por nombre o código de diagnóstico. La búsqueda es parcial (substring) y usualmente sin distinguir mayúsculas/minúsculas.
    - Ejemplos válidos: `q=lumba`, `q=DX0`, `q=1`.
    - Si `q=1` te devuelve 2 diagnósticos es normal: probablemente ambos contienen el dígito "1" en su código o nombre.
    - Si no hay coincidencias, la API responde 200 con una lista vacía (esto es esperado; no es error).
    - Paginación y otros filtros siguen las convenciones de DRF si están habilitados.

- patients
  - GET http://localhost:8000/api/patients/patients/?page={n}
    
    Nota: `page={n}` indica el número de página a retornar. Comienza en 1. Si omites `page`, devuelve la primera página por defecto.
  - POST http://localhost:8000/api/patients/patients/
    
    Body (JSON):
    ```json
    {
      "document_number": "12345678",
      "paternal_lastname": "Perez",
      "maternal_lastname": "Lopez",
      "name": "Juan",
      "email": "juan.perez@example.com",
      "ocupation": "Estudiante",
      "health_condition": "Sin antecedentes",
      "document_type_id": 1,
      "region_code": 1,
      "province_code": 101,
      "district_code": 10101,
      "sex": "M",
      "phone1": "999999999",
      "address": "Av. Siempre Viva 123",
      "reflexo_id": 1
    }
    ```
    Notas:
    - Campos obligatorios: `document_number`, `paternal_lastname`, `name`, `email`, `ocupation`, `health_condition`, `document_type_id` y ubicación (`region_id/province_id/district_id` o alternativamente `region_code/province_code/district_code`).
    - `maternal_lastname` es requerido por el serializer; incluye un valor si tu flujo lo exige.
    - `sex`, `phone1`, `phone2`, `address`, `birth_date` son opcionales.
    - Si usas códigos ubigeo (como en el ejemplo), envía `region_code/province_code/district_code` y el backend resolverá los IDs. Si prefieres usar IDs, envía `region_id/province_id/district_id` (deben existir en Ubi Geo).
    - Jerarquía: la `province` debe pertenecer a la `region` elegida; el `district` debe pertenecer a la `province` elegida.
    - Muy importante si usas IDs: `region_id`, `province_id` y `district_id` deben ser el campo `id` (primary key) devuelto por los endpoints de Ubi Geo; NO uses `ubigeo_code` ni `sequence` en esos campos.
    - Cómo obtener IDs válidos:
      - Regiones: `GET /api/locations/regions/`
      - Provincias por región: `GET /api/locations/provinces/?region={region_id}`
      - Distritos por provincia: `GET /api/locations/districts/?province={province_id}`
      - Tipos de documento: `GET /api/configurations/document_types/`
    - Multitenant (empresa/tenant): si tu usuario no tiene tenant asignado o eres admin global, debes enviar `reflexo_id` (ID de la empresa) en el body.
    
  - GET http://localhost:8000/api/patients/patients/{id}/
  - PUT http://localhost:8000/api/patients/patients/{id}/
    
    Body (JSON) ejemplo (PUT = actualización completa, incluye todos los campos requeridos):
    ```json
    {
      "document_number": "12345678",
      "paternal_lastname": "Perez",
      "maternal_lastname": "Lopez",
      "name": "Juan",
      "email": "juan.perez@example.com",
      "ocupation": "Estudiante",
      "health_condition": "Sin antecedentes",
      "document_type_id": 1,
      "region_code": 1,
      "province_code": 101,
      "district_code": 10101,
      "sex": "M",
      "phone1": "999999999",
      "address": "Av. Siempre Viva 123"
    }
    ```
    Notas:
    - PUT requiere enviar todos los campos obligatorios del paciente; si omites alguno, obtendrás 400 con "This field is required".
    - Para ubicación puedes usar `region_id/province_id/district_id` (IDs de Ubi Geo) o `region_code/province_code/district_code` (códigos ubigeo), igual que en el POST.
    - Unicidad: `document_number` y `email` deben ser únicos. Si deseas actualizar estos campos, debes cambiarlos a valores que no estén registrados en otro paciente; de lo contrario obtendrás 400 por duplicado.
    - Si no vas a cambiar `document_number` y/o `email`, considera usar PATCH y no incluir esos campos para evitar errores de unicidad.
    - Si solo deseas modificar algunos campos, usa PATCH.
  
  - PATCH http://localhost:8000/api/patients/patients/{id}/
    
    Body (JSON) ejemplo (actualización parcial):
    ```json
    {
      "phone1": "988888888",
      "address": "Av. Siempre Viva 742"
    }
    ```
  - DELETE http://localhost:8000/api/patients/patients/{id}/
  - GET http://localhost:8000/api/patients/patients/search/?q={text}&page={n}

- medical records
  - GET http://localhost:8000/api/patients/medical-records/
  - POST http://localhost:8000/api/patients/medical-records/
    
    Body (JSON):
    ```json
    {
      "patient_id": 4,
      "diagnose_id": 5,
      "diagnosis_date": "2025-09-04",
      "notes": "Notas"
    }
    ```
    Notas:
    - Usa IDs reales:
      - `patient_id`: ID del paciente (creado previamente en `/api/patients/patients/`).
      - `diagnose_id`: ID del diagnóstico (consulta `/api/patients/diagnoses/`).
    - Campos requeridos: `patient_id`, `diagnose_id`, `diagnosis_date`.
    - Multitenant:
      - Si eres usuario de empresa (no admin), el `patient` y el `diagnose` deben pertenecer a tu empresa. Si tu usuario no tiene empresa asignada, envía `reflexo_id` en el body.
      - Si eres admin global, no se aplica filtro por empresa; si no envías `reflexo_id`, el backend intentará inferirlo desde el `patient`.
    - Unicidad por trío: el modelo exige que `(patient_id, diagnose_id, diagnosis_date)` sea único. Si obtienes 400 por conjunto único:
      - Usa otra `diagnosis_date` (no futura), o
      - Crea/usa un `diagnose_id` distinto (por ejemplo, crea un nuevo diagnóstico en `/api/patients/diagnoses/`).
    - Ejemplos de campos opcionales según tu modelo: `symptoms`, `treatment`, `notes`, `status`.
  - GET http://localhost:8000/api/patients/medical-records/{id}/
  - PUT http://localhost:8000/api/patients/medical-records/{id}/
  - DELETE http://localhost:8000/api/patients/medical-records/{id}/
  - GET http://localhost:8000/api/patients/patients/{patient_id}/medical-history/
  - GET http://localhost:8000/api/patients/diagnosis-statistics/?from=YYYY-MM-DD&to=YYYY-MM-DD


---

## Architect Module
Base: http://localhost:8000/api/architect/

- login
  - POST http://localhost:8000/api/architect/auth/login/


Pruebas en Postman (login)
- POST http://localhost:8000/api/architect/auth/login/
    
    Body (JSON):
    ```json
    {
      "email": "admin@gmail.com",
      "password": "admin123456"
    }
    ```
  
  - POST http://localhost:8000/api/architect/auth/login/
    
    Body (JSON):
    ```json
    {
      "email": "senati@gmail.com",
      "password": "wilber123456"
    }
    ```
  
  - POST http://localhost:8000/api/architect/auth/login/
    
    Body (JSON):
    ```json
    {
      "email": "prueba2@gmail.com",
      "password": "clinica23456"
    }
    ```

---

## Therapists Module
Base: http://localhost:8000/api/therapists/
Router resource: `therapists`

- standard
  - GET http://localhost:8000/api/therapists/therapists/ (filters: `active=true|false`, `region`, `province`, `district`, `search`)
  - POST http://localhost:8000/api/therapists/therapists/
    
    Body (JSON):
    ```json
    {
      "document_type_id": 1,
      "document_number": "12345678",
      "last_name_paternal": "Pérez",
      "last_name_maternal": "García",
      "first_name": "Ana",
      "email": "ana.perez@gmail.com",
      "region_id": 1,
      "province_id": 10,
      "district_id": 1001
    }
    ```
    Notas:
    - Campos requeridos: `document_type_id`, `document_number`, `last_name_paternal`, `last_name_maternal`, `first_name`, `email`, `region_id`, `province_id`, `district_id`.
    - Identificadores de ubicación:
      - Opción A (IDs): `region_id`, `province_id`, `district_id` son los IDs reales (PK) de cada tabla. Obténlos así:
        - Regiones: `GET /api/locations/regions/` → usa el campo `id`.
        - Provincias por región: `GET /api/locations/provinces/?region={region_id}` → usa el campo `id`.
        - Distritos por provincia: `GET /api/locations/districts/?province={province_id}` → usa el campo `id`.
      - Opción B (Códigos ubigeo): puedes enviar `region_code`, `province_code`, `district_code` (códigos ubigeo) y la API los resolverá automáticamente a los IDs correctos. Si usas `*_code`, no es necesario enviar los `*_id`.
      - Regla de coherencia: la `province` debe pertenecer a la `region`; el `district` debe pertenecer a la `province`.
    - Ejemplo usando códigos ubigeo:
      ```json
      {
        "document_type_id": 1,
        "document_number": "12345678",
        "last_name_paternal": "Pérez",
        "last_name_maternal": "García",
        "first_name": "Ana",
        "email": "ana.perez@gmail.com",
        "region_code": 1,
        "province_code": 101,
        "district_code": 10101
      }
      ```
    - `email` debe ser válido y terminar en `@gmail.com`.
    - `document_number` es único.
    - Coherencia: la `province` debe pertenecer a la `region`; el `district` debe pertenecer a la `province`.
  - GET http://localhost:8000/api/therapists/therapists/{id}/
  - PUT/PATCH http://localhost:8000/api/therapists/therapists/{id}/
    
    Notas (PUT):
    - En este proyecto, `PUT` se comporta como actualización parcial (igual que `PATCH`).
    - Puedes enviar solo los campos a modificar; no es obligatorio enviar todos los requeridos.
    
    Ejemplo (PUT: solo cambiar email):
    ```json
    {
      "email": "nuevo.correo@gmail.com"
    }
    ```

    Ejemplo (PUT: cambiar ubicación usando códigos ubigeo):
    ```json
    {
      "region_code": 1,
      "province_code": 101,
      "district_code": 10101
    }
    ```
  - DELETE http://localhost:8000/api/therapists/therapists/{id}/ (soft delete)

- custom actions
  - GET http://localhost:8000/api/therapists/therapists/inactive/
  - POST or PATCH http://localhost:8000/api/therapists/therapists/{id}/restore/
    
    Body (JSON):
    ```json
    {}
    ```


---

## Appointments & Status Module
Base: http://localhost:8000/api/appointments/
Router resources: `appointments`, `appointment-statuses`, `tickets`

- appointments
  - GET http://localhost:8000/api/appointments/appointments/ (filters: see view; supports search, ordering, pagination)
  - POST http://localhost:8000/api/appointments/appointments/
    
    Body (JSON):
    ```json
    {
      "patient": 1,
      "therapist": 1,
      "appointment_date": "2025-01-20",
      "hour": "10:00"
    }
    ```
    Notas:
    - `patient` y `therapist` deben ser IDs que existan previamente (FK válidas).
    - `history` es opcional; si no lo envías, el sistema buscará uno activo del paciente y, si no existe, creará uno mínimo automáticamente.
    - Formatos admitidos:
      - `appointment_date`: `YYYY-MM-DD` (o ISO con fecha/hora)
      - `hour`: `HH:MM`
  - GET http://localhost:8000/api/appointments/appointments/{id}/
  - PUT/PATCH http://localhost:8000/api/appointments/appointments/{id}/
  - DELETE http://localhost:8000/api/appointments/appointments/{id}/
  - Custom actions:
    - GET http://localhost:8000/api/appointments/appointments/completed/
    - GET http://localhost:8000/api/appointments/appointments/pending/
    - GET http://localhost:8000/api/appointments/appointments/by_date_range/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    - GET http://localhost:8000/api/appointments/appointments/check_availability/?date=YYYY-MM-DD&hour=HH:MM
    - POST http://localhost:8000/api/appointments/appointments/{id}/cancel/
      
      Body (JSON):
      ```json
      {}
      ```
    - POST http://localhost:8000/api/appointments/appointments/{id}/reschedule/
      
      Body (JSON):
      ```json
      {
        "appointment_date": "2025-01-22",
        "hour": "11:00"
      }
      ```

- appointment statuses
  - GET http://localhost:8000/api/appointments/appointment-statuses/
  - POST http://localhost:8000/api/appointments/appointment-statuses/
    
    Body (JSON):
    ```json
    {
      "name": "CONFIRMADO",
      "description": "Estado confirmado"
    }
    ```
  - PUT/PATCH http://localhost:8000/api/appointments/appointment-statuses/{id}/
    
    Notas:
    - PUT requiere cuerpo completo (por ejemplo, `name` es obligatorio). Si envías solo `description` sin `name`, obtendrás 400.
    - PATCH es actualización parcial; puedes enviar solo los campos que desees modificar.
    
    Ejemplo (PUT: cuerpo completo requerido):
    ```json
    {
      "name": "CONFIRMADO",
      "description": "Estado confirmado actualizado"
    }
    ```
  - GET http://localhost:8000/api/appointments/appointment-statuses/{id}/
  - PUT/PATCH http://localhost:8000/api/appointments/appointment-statuses/{id}/
  - DELETE http://localhost:8000/api/appointments/appointment-statuses/{id}/
  - Custom actions:
    - POST http://localhost:8000/api/appointments/appointment-statuses/{id}/activate/
      
      Body (JSON):
      ```json
      {}
      ```
    - POST http://localhost:8000/api/appointments/appointment-statuses/{id}/deactivate/
      
      Body (JSON):
      ```json
      {}
      ```

- tickets
  - GET http://localhost:8000/api/appointments/tickets/
  - POST http://localhost:8000/api/appointments/tickets/
    
    Body (JSON):
    ```json
    {
      "appointment": 1,
      "amount": 100.0,
      "payment_method": "cash"
    }
    ```
  - GET http://localhost:8000/api/appointments/tickets/{id}/
  - PUT/PATCH http://localhost:8000/api/appointments/tickets/{id}/
  - DELETE http://localhost:8000/api/appointments/tickets/{id}/
  - Custom actions:
    - POST http://localhost:8000/api/appointments/tickets/{id}/mark_as_paid/
    - POST http://localhost:8000/api/appointments/tickets/{id}/mark_paid/ (alias)
      
      Body (JSON):
      ```json
      {}
      ```
    - POST http://localhost:8000/api/appointments/tickets/{id}/mark_as_cancelled/
    - POST http://localhost:8000/api/appointments/tickets/{id}/cancel/ (alias)
      
      Body (JSON):
      ```json
      {}
      ```
    - GET http://localhost:8000/api/appointments/tickets/by_payment_method/?payment_method={method}
      
      Notas:
      - También puedes usar el alias `method` en lugar de `payment_method`.
      - Ejemplo: `/api/appointments/tickets/by_payment_method/?method=efectivo`
    - GET http://localhost:8000/api/appointments/tickets/by_number/?number={ticket_no}
      
      Notas:
      - Parámetro requerido: `number` (alias: `ticket_number`).
      - Devuelve 404 si el número no existe o pertenece a otro tenant (para usuarios no admin).
      - Ejemplo: `/api/appointments/tickets/by_number/?number=TKT-001`
      - Uso: obtener un ticket específico por su número. Si el número no existe o no pertenece al tenant actual, se devuelve un error 404.

---

## Histories & Configurations Module
Base: http://localhost:8000/api/configurations/

- histories
  - GET http://localhost:8000/api/configurations/histories/
  - POST http://localhost:8000/api/configurations/histories/create/
    
    Body (JSON):
    ```json
    { "patient": 4 }
    ```
    Notas:
    - `patient` debe ser el ID de un paciente existente y activo.
    - Para usuarios no admin, el paciente debe pertenecer a la misma empresa (tenant).
    - Si ya existe un historial activo para el paciente, retorna 409 con `existing_history_id`.
  - POST http://localhost:8000/api/configurations/histories/{id}/delete/
    
    Notas:
    - Elimina el historial de forma definitiva (hard delete). Respuesta: 204 No Content.
    - Requiere que el historial pertenezca a tu empresa (tenant) si no eres admin.

- document types
  - GET http://localhost:8000/api/configurations/document_types/
  - POST http://localhost:8000/api/configurations/document_types/create/
    
    Body (JSON) (usuario con tenant):
    ```json
    {
      "name": "Factura"
    }
    ```
    Body (JSON) (admin sin tenant - especificar empresa):
    ```json
    {
      "name": "Factura",
      "reflexo_id": 1
    }
    ```
    Notas:
    - Los tipos de documento son globales (no multitenant en BD). Si tu usuario no tiene empresa asignada, puedes indicar `reflexo_id` para documentar a qué empresa corresponde la operación.
    - Si tu usuario tiene empresa, no es necesario enviar `reflexo_id`.
  - DELETE http://localhost:8000/api/configurations/document_types/{id}/delete/
    
    Nota: eliminación definitiva (hard delete). Respuesta: 200 con `{ "status": "deleted" }`.

- payment types
  - GET http://localhost:8000/api/configurations/payment_types/
  - DELETE http://localhost:8000/api/configurations/payment_types/{id}/delete/
    
    Nota: eliminación definitiva (hard delete). Respuesta: 204 No Content.
  - POST http://localhost:8000/api/configurations/payment_types/create/
    
    Body (JSON):
    ```json
    {
      "name": "Efectivo"
    }
    ```
    Notas:
    - Los tipos de pago son globales (no multitenant en BD). Este endpoint solo requiere `name`.
    - Cualquier `reflexo_id` enviado será ignorado.
  - PUT http://localhost:8000/api/configurations/payment_types/{id}/edit/

---

## Locations Module (Ubi Geo)
Base: http://localhost:8000/api/locations/
Router resources: `regions`, `provinces`, `districts`

- regions
  - GET http://localhost:8000/api/locations/regions/
    
    Nota: usa el campo `id` de cada región como `region_id` en la creación de pacientes. `ubigeo_code` es solo informativo.
  - GET http://localhost:8000/api/locations/regions/{id}/

- provinces
  - GET http://localhost:8000/api/locations/provinces/?region={region_id}
  - GET http://localhost:8000/api/locations/provinces/{id}/
  
    Notas de uso:
    - Filtro por región: usa `?region=<id_entero>` sin llaves. Ejemplos válidos: `?region=1`, `?region= 1 `.
      - El backend también tolera accidentalmente `?region={1}` (con llaves), pero la forma correcta es SIN llaves.
    - Detalle: `GET /api/locations/provinces/{id}/` donde `{id}` es el ID (entero) de la provincia.
    - Multitenant: la lista está filtrada por empresa (tenant) del usuario autenticado; administradores globales verán datos globales.
    - Usa el campo `id` devuelto para `province_id` cuando crees/edites entidades que referencian provincias.
    - Coherencia: asegúrate de que la provincia pertenezca a la `region_id` que elegiste.

    Ejemplos rápidos:
    - Listar provincias por región 1:
      - GET `http://localhost:8000/api/locations/provinces/?region=1`
    - Obtener detalle de provincia 592 (ejemplo real validado):
      - GET `http://localhost:8000/api/locations/provinces/592/`

    Troubleshooting (404 Not Found en detalle):
    - Autenticación: asegúrate de enviar `Authorization: Bearer <token>`.
    - Multitenant: el endpoint filtra por empresa (tenant). Si tu usuario no es admin global y el registro `id={id}` pertenece a otra empresa (campo `reflexo` distinto) o tu usuario no tiene tenant asignado, no lo verás y retornará 404. Los administradores globales ven todos.
    - Globales: si tu usuario no tiene tenant, solo verás registros globales (`reflexo IS NULL`).
    - Soft delete: si la provincia tiene `deleted_at` con valor, no aparece y el detalle también dará 404.
    - El ID no existe: valida primero con el listado.
    - Nota práctica: si usas un ID real como `592` y tu usuario tiene acceso (por tenant o global), el detalle responderá correctamente.

    ¿Cómo encontrar un ID válido para el detalle?
    1) Primero lista por región que sabes que existe: `GET /api/locations/regions/` para obtener un `region_id`.
    2) Luego: `GET /api/locations/provinces/?region=<region_id>` y toma un `id` de la respuesta.
    3) Usa ese `id` en: `GET /api/locations/provinces/{id}/`.

- districts
  - GET http://localhost:8000/api/locations/districts/?province={province_id}
  - GET http://localhost:8000/api/locations/districts/{id}/
  
    Notas de uso:
    - Filtro por provincia: usa `?province=<id_entero>` sin llaves. Ejemplos válidos: `?province=10`, `?province= 10 `.
      - Evita `?province={10}` con llaves; aunque a veces puede funcionar, no es la forma recomendada.
    - Detalle: `GET /api/locations/districts/{id}/` donde `{id}` es el ID (entero) del distrito.
    - Multitenant: la lista y el detalle están filtrados por empresa (tenant) del usuario autenticado; administradores globales verán también los globales (`reflexo IS NULL`).
    - Soft delete: solo se listan registros con `deleted_at IS NULL`.
    - Usa el campo `id` devuelto para `district_id` cuando referencies distritos en otros módulos.

    - Obtener detalle de distrito 5876 (ejemplo real validado):
      - GET `http://localhost:8000/api/locations/districts/5876/`

    Troubleshooting (404 Not Found en detalle):
    - Autenticación: incluye `Authorization: Bearer <token>`.
    - Multitenant: si el registro pertenece a otro tenant (campo `reflexo` distinto) o tu usuario no tiene tenant y el distrito no es global, verás 404.
    - Soft delete: si `deleted_at` tiene valor, no estará disponible.
    - El ID no existe o no es visible: primero obtén un ID con el listado filtrado por `province` y luego úsalo en el detalle.
    - Nota práctica: si usas un ID real como `5876` y tu usuario tiene acceso (por tenant o global), el detalle responderá correctamente.

 

---

## Company Reports Module
Base: http://localhost:8000/api/company/
Router resources: `statistics`, `company`

- statistics
  - GET http://localhost:8000/api/company/statistics/metricas/?start=YYYY-MM-DD&end=YYYY-MM-DD (custom action del ViewSet)
  - GET http://localhost:8000/api/company/reports/statistics/?start=YYYY-MM-DD&end=YYYY-MM-DD (APIView directa)

    Notas:
    - Ambos endpoints requieren los parámetros `start` y `end` con formato `YYYY-MM-DD`.
    - Si `start > end` devolverá 400; si el formato es inválido, también 400.
    - Responden métricas agregadas desde `StatisticsService` serializadas con `StatisticsResource`.
    - Cómo llamarlo en Postman: usa Params -> `start=2025-01-01`, `end=2025-01-31` y Header `Authorization: Bearer <token>`.
    - También puedes pasarlo por querystring en la URL (reemplazando las fechas por valores reales), sin usar placeholders literales.

- company
  - GET http://localhost:8000/api/company/company/
  - POST http://localhost:8000/api/company/company/
    
    Body (JSON):
    ```json
    {
      "company_name": "Mi Empresa"
    }
    ```
    Notas:
    - El modelo `company_reports/models/company.py` define el campo `company_name` (no `name`).
    - No existe campo `ruc` en `CompanyData`; si necesitas RUC, debería agregarse al modelo/serializer en otra tarea.
    - Este POST crea a través del `ModelViewSet` estándar y NO asigna `reflexo` automáticamente. Si tu usuario no es admin global, puede que luego no veas el registro en el listado por el filtro de tenant.
    - Recomendado para multitenant: usa `POST /api/company/company/store/` que asigna el tenant automáticamente.

  - POST http://localhost:8000/api/company/company/store/
    Body (JSON):
    ```json
    {
      "company_name": "Mi Empresa"
    }
    ```
    Notas:
    - Asigna `reflexo` desde tu token (tenant actual) usando `assign_tenant_on_create`.
    - Si tu usuario es admin global y no tiene tenant, `reflexo` quedará null.
  - GET http://localhost:8000/api/company/company/{id}/
  - PUT/PATCH http://localhost:8000/api/company/company/{id}/
    Body (JSON):
    ```json
    {
      "company_name": "Nuevo nombre"
    }
    ```
    Notas:
    - El servicio `CompanyService.store()` valida que `company_name` sea obligatorio incluso en PATCH; si no lo envías, retornará 400 "El nombre de la empresa es requerido".
    - Este update utiliza `assign_tenant_on_create` para asegurar coherencia de tenant; el listado está filtrado por tenant.
  - DELETE http://localhost:8000/api/company/company/{id}/
    Notas:
    - Eliminación definitiva (hard delete). No deja registros residuales.
    - Respuesta 200 con mensaje de éxito (ver `CompanyDataViewSet.destroy()` en `company_reports/views/company_views.py`).
    - Sujetos a filtrado por tenant: solo puedes eliminar empresas visibles para tu token. Los administradores globales pueden eliminar cualquier registro.
  - Custom actions (file/logo)
    - POST http://localhost:8000/api/company/company/{id}/upload_logo/ (acepta JSON o multipart/form-data)
      
      Body requerido (JSON o form-data):
      ```json
      {
        "company_logo": "<ruta_o_URL_del_logo>"
      }
      ```
      Notas:
      - Si ya existe un logo, este POST devuelve 400 con: "La empresa ya tiene un logo. Use PUT para actualizar." Usa PUT para reemplazarlo.
      - Si falta `company_logo`, devuelve 400: "Se requiere la URL del logo".

    - PUT http://localhost:8000/api/company/company/{id}/upload_logo/
      
      Body requerido (JSON o form-data):
      ```json
      {
        "company_logo": "<ruta_o_URL_del_logo>"
      }
      ```
      Notas:
      - Actualiza/reemplaza el logo existente.

    - DELETE http://localhost:8000/api/company/company/{id}/delete_logo/
    - GET http://localhost:8000/api/company/company/{id}/show/
      Notas:
      - Ruta correcta según `company_reports/urls.py`: acción `show` en `CompanyDataViewSet`.
      - Requiere `Authorization: Bearer <token>` y que el `{id}` exista y sea visible para tu tenant.
      - Incluye el slash final. Si `{id}` está vacío o no es visible por tenant, verás 404.

- reports (JSON)
  - GET http://localhost:8000/api/company/reports/appointments-per-therapist/?from=YYYY-MM-DD&to=YYYY-MM-DD&therapist_id={id}
  - GET http://localhost:8000/api/company/reports/patients-by-therapist/?from=YYYY-MM-DD&to=YYYY-MM-DD&therapist_id={id}
  - GET http://localhost:8000/api/company/reports/daily-cash/?date=YYYY-MM-DD
    Notas:
    - Reemplaza `YYYY-MM-DD` por una fecha real (ej.: `2025-01-31`). No uses el placeholder literal ni otro formato.
    - Este endpoint valida el parámetro `date` con `DateParameterSerializer` (formato ISO `YYYY-MM-DD`). Si no coincide, devuelve 400 con mensaje de formato.
  - GET http://localhost:8000/api/company/reports/improved-daily-cash/?date=YYYY-MM-DD
    Notas:
    - Reemplaza `YYYY-MM-DD` por una fecha real (ej.: `2025-01-31`).
    - Valida el parámetro `date` con formato ISO `YYYY-MM-DD`; si no coincide, devuelve 400.
  - GET http://localhost:8000/api/company/reports/daily-paid-tickets/?date=YYYY-MM-DD
    Notas:
    - Reemplaza `YYYY-MM-DD` por una fecha real (ej.: `2025-01-31`).
    - Valida el parámetro `date` con formato ISO `YYYY-MM-DD`; si no coincide, devuelve 400.
  - GET http://localhost:8000/api/company/reports/appointments-between-dates/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    Notas:
    - Usa exactamente `start_date` y `end_date` (no `from`/`to`).
    - Ambos deben ir en formato ISO `YYYY-MM-DD` y `start_date <= end_date`, de lo contrario devuelve 400.

- exports (files)
  - GET http://localhost:8000/api/company/exports/pdf/citas-terapeuta/?date=YYYY-MM-DD
    Notas:
    - Reemplaza `YYYY-MM-DD` por una fecha real. Requiere Header `Authorization: Bearer <token>`.
    - Respuesta: archivo PDF (descarga). Filtrado por tenant.
  - GET http://localhost:8000/api/company/exports/pdf/pacientes-terapeuta/?date=YYYY-MM-DD
    Notas:
    - Reemplaza `YYYY-MM-DD` por una fecha real. Requiere Header `Authorization: Bearer <token>`.
    - Respuesta: archivo PDF (descarga). Filtrado por tenant.
  - GET http://localhost:8000/api/company/exports/pdf/resumen-caja/?date=YYYY-MM-DD
    Notas:
    - Reemplaza `YYYY-MM-DD` por una fecha real. Requiere Header `Authorization: Bearer <token>`.
    - Respuesta: archivo PDF (descarga) con total calculado. Filtrado por tenant.
  - GET http://localhost:8000/api/company/exports/pdf/caja-chica-mejorada/?date=YYYY-MM-DD
    Notas:
    - Reemplaza `YYYY-MM-DD` por una fecha real. Requiere Header `Authorization: Bearer <token>`.
    - Respuesta: archivo PDF (descarga). Filtrado por tenant.
  - GET http://localhost:8000/api/company/exports/pdf/tickets-pagados/?date=YYYY-MM-DD
    Notas:
    - Reemplaza `YYYY-MM-DD` por una fecha real. Requiere Header `Authorization: Bearer <token>`.
    - Respuesta: archivo PDF (descarga). Filtrado por tenant.
  - GET http://localhost:8000/api/company/exports/excel/citas-rango/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
    Notas:
    - Usa exactamente `start_date` y `end_date` (formato `YYYY-MM-DD`). Requiere Header `Authorization: Bearer <token>`.
    - Respuesta: archivo Excel (descarga). Filtrado por tenant.
  - GET http://localhost:8000/api/company/exports/excel/caja-chica-mejorada/?date=YYYY-MM-DD
    Notas:
    - Reemplaza `YYYY-MM-DD` por una fecha real. Requiere Header `Authorization: Bearer <token>`.
    - Respuesta: archivo Excel (descarga). Filtrado por tenant.
  - GET http://localhost:8000/api/company/exports/excel/tickets-pagados/?date=YYYY-MM-DD
    Notas:
    - Reemplaza `YYYY-MM-DD` por una fecha real. Requiere Header `Authorization: Bearer <token>`.
    - Respuesta: archivo Excel (descarga). Filtrado por tenant.

 

---

## Global Headers and Auth
- Authorization: `Bearer {{token}}`
- Content-Type: `application/json` (unless multipart/form-data)

## Environment Variables for Postman
- `BASE_URL`: `http://localhost:8000` (examples already use absolute URLs)
- `token`: JWT access token

## Change Log
- v1.0 Initial extraction from `urls.py` and views across modules.
