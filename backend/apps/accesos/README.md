# App `accesos` — Accesos y Permisos

Esta app implementa control de roles, delegación UGEL, auditoría básica y un mock para recuperación de contraseña.

Contenido
- Modelos: `AuditLog`, `UGELDelegation`, `PasswordResetMock`, `Period` (demo).
- Permisos: `RolePermission`, `CanManageUGEL`.
- Decoradores: `ensure_not_closed` para evitar edición tras cierre (devuelve 409).
- Endpoints (vistas): delegación UGEL, gestión UGEL, cierre de periodo, export (mock), password reset (mock).

---

Modelos principales

- `AuditLog` — registra acciones relevantes (actor, acción, target, timestamp, metadata).
- `UGELDelegation` — registro que indica que la Directora delegó en un Tutor para gestionar UGEL.
- `PasswordResetMock` — token temporal para pruebas de recuperación de contraseña (no envía emails).
- `Period` — modelo demo para representar mes/bimestre y permitir probar el cierre (si ya tienes un modelo similar, sustituir).

Permisos y helpers

- `get_user_role(user)` (en `utils.py`): intenta obtener el rol del usuario de forma flexible (campo `role` directo, `profile.role` o primer `Group`).
- `RolePermission` (en `permissions.py`): las vistas pueden definir `allowed_roles = ['Directora', 'Coordinador', ...]` y el permiso lo respeta.
- `CanManageUGEL`: permite a la Directora siempre y al Tutor sólo si hay una `UGELDelegation` activa.
- `ensure_not_closed(get_instance_fn)` (en `decorators.py`): decorador para endpoints que modifican recursos; mira si la entidad está cerrada y devuelve 409 si es así.

Rutas / Endpoints

Todas las rutas están expuestas bajo `/accesos/` (ej.: `/accesos/ugel/delegate/`).

- POST `/accesos/ugel/delegate/` — Directora delega a un Tutor. Body: `{"tutor_id": <id>}`. Respuestas: 201 creado.
- GET `/accesos/ugel/manage/` — Acceso protegido para gestión UGEL. Retorna 200 si el usuario tiene permiso.
- POST `/accesos/period/<period_id>/close/` — Cierra un periodo (solo Directora/Coordinador). Si ya está cerrado devuelve 409.
- GET `/accesos/export/pdf/<report_id>/` — Mock de export (registra auditoría).
- POST `/accesos/auth/password-reset/` — Request mock de reset. Body: `{"email": "..."}`. Respuestas: 201 con `token` en el cuerpo (NO se envía email).
- POST `/accesos/auth/password-reset/confirm/` — Confirmar reset. Body: `{"token": "<uuid>", "password": "<newpass>"}`.

Notas sobre permisos en endpoints

- Las vistas usan `permission_classes = [RolePermission]` o `CanManageUGEL` según corresponda.
- `PasswordReset*` endpoints permiten `AllowAny` (pueden ser llamados sin autenticación) y devuelven token para pruebas.

Auditoría

- Las acciones importantes (delegate_ugel, close_period, export_pdf, password_reset) crean registros en `AuditLog`.
- La auditoría es mínima (actor, acción, target_type, target_id, metadata opcional). Puedes extender `metadata` con filtros/params si lo deseas.

Ejemplos rápidos (usando `curl` local y sesión autenticada)

1) Delegar UGEL (Directora):

```bash
curl -X POST -H "Content-Type: application/json" -u directora:pass \
  -d '{"tutor_id": 3}' http://localhost:8000/accesos/ugel/delegate/
```

2) Pedir reset de contraseña (mock):

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"email": "tutor@example.com"}' http://localhost:8000/accesos/auth/password-reset/
# la respuesta contendrá el token en JSON (solo para testing)
```

Comandos útiles (en el entorno del proyecto)

Usando el Python del virtualenv del workspace:

```bash
# Generar migraciones para accesos (crea archivos en repo)
/workspaces/sistema-intranet-colegio/.venv/bin/python /workspaces/sistema-intranet-colegio/backend/manage.py makemigrations apps.accesos

# Aplicar migraciones (a la DB local)
/workspaces/sistema-intranet-colegio/.venv/bin/python /workspaces/sistema-intranet-colegio/backend/manage.py migrate

# Ejecutar solo tests de la app accesos
/workspaces/sistema-intranet-colegio/.venv/bin/python /workspaces/sistema-intranet-colegio/backend/manage.py test apps.accesos

# Ejecutar todo el test suite
/workspaces/sistema-intranet-colegio/.venv/bin/python /workspaces/sistema-intranet-colegio/backend/manage.py test
```

Notas finales y recomendaciones

- Si el proyecto ya tiene modelos para Period/meses o un esquema de roles distinto, sustituir el `Period` demo y adaptar `get_user_role` según corresponda.
- Para un flujo de recuperación de contraseña en producción, integrar un backend de email y reemplazar el mock por un mecanismo que envíe el token por correo (por ejemplo usar Django's PasswordResetTokenGenerator y el sistema de email del proyecto).

---

Este documento describe el comportamiento implementado; ajustes adicionales (migraciones, adaptaciones a modelos existentes, o cambios en permisos) deben realizarse según las necesidades del proyecto.
