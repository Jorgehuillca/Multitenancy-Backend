import json
from django.http import JsonResponse, HttpResponseNotAllowed
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from ..models.history import History
from ..models.document_type import DocumentType
from architect.utils.tenant import filter_by_tenant, get_tenant, is_global_admin
from patients_diagnoses.models.patient import Patient

@csrf_exempt
@api_view(["GET"])
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def histories_list(request, pk=None):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    
    # Si se proporciona pk, devolver un historial específico
    if pk is not None:
        try:
            base = History.objects.filter(deleted_at__isnull=True).select_related("patient")
            if not is_global_admin(request.user):
                base = filter_by_tenant(base, request.user, field='reflexo')
            h = base.get(pk=pk)
            return JsonResponse({
                "id": h.id,
                "local_id": getattr(h, 'local_id', None),
                "patient": h.patient_id,
                "patient_name": f"{h.patient.name} {h.patient.paternal_lastname}" if h.patient else None,
                "reflexo_id": getattr(h, 'reflexo_id', None),
                "testimony": h.testimony,
                "private_observation": h.private_observation,
                "observation": h.observation,
                "height": float(h.height) if h.height is not None else None,
                "weight": float(h.weight) if h.weight is not None else None,
                "last_weight": float(h.last_weight) if h.last_weight is not None else None,
                "menstruation": h.menstruation,
                "diu_type": h.diu_type,
                "gestation": h.gestation,
                "created_at": h.created_at.isoformat() if h.created_at else None,
                "updated_at": h.updated_at.isoformat() if h.updated_at else None
            })
        except History.DoesNotExist:
            return JsonResponse({"error": "No encontrado"}, status=404)
    
    # Aislamiento por tenant
    qs = History.objects.filter(deleted_at__isnull=True).select_related("patient")
    # Bypass solo para admins globales
    if not is_global_admin(request.user):
        qs = filter_by_tenant(qs, request.user, field='reflexo')

    data = [{
        "id": h.id,
        "local_id": getattr(h, 'local_id', None),
        "patient": h.patient_id,
        "patient_name": f"{h.patient.name} {h.patient.paternal_lastname}" if h.patient else None,
        "reflexo_id": getattr(h, 'reflexo_id', None)
    } for h in qs]
    return JsonResponse({"histories": data})

@csrf_exempt
@api_view(["POST"])
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def history_create(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    
    try:
        payload = json.loads(request.body.decode())
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)
    
    patient_id = payload.get("patient")
    tenant_id = get_tenant(request.user)

    # Validar campos obligatorios
    if patient_id is None:
        return JsonResponse({"error": "Campos obligatorios faltantes"}, status=400)

    # Verificar si ya existe un historial activo para este paciente
    # 1) Buscar paciente activo (no eliminado)
    try:
        patient = Patient.objects.get(pk=patient_id, deleted_at__isnull=True)
    except Patient.DoesNotExist:
        return JsonResponse({"error": "Paciente no encontrado"}, status=404)

    # 2) Validar tenant para usuarios no-admin
    if not is_global_admin(request.user):
        # Paciente debe pertenecer al mismo tenant del usuario (si el usuario tiene tenant asignado)
        user_tenant = tenant_id
        if user_tenant is not None and patient.reflexo_id != user_tenant:
            return JsonResponse({"error": "Paciente no pertenece a tu empresa"}, status=403)

    existing_history = filter_by_tenant(
        History.objects.filter(deleted_at__isnull=True),
        request.user,
        field='reflexo'
    ).filter(patient_id=patient_id).first()
    
    if existing_history:
        return JsonResponse({
            "error": "Ya existe un historial activo para este paciente",
            "existing_history_id": existing_history.id
        }, status=409)
    
    # Alinear tenant: si el usuario admin global no trae tenant, usar el del paciente
    if tenant_id is None and hasattr(patient, 'reflexo_id'):
        tenant_id = patient.reflexo_id
    if tenant_id is None:
        return JsonResponse({"error": "No se pudo determinar el tenant para crear el historial"}, status=400)

    try:
        # Asignar local_id secuencial por tenant
        from django.db.models import Max
        from django.db import transaction, IntegrityError
        with transaction.atomic():
            max_local = (
                History.objects.select_for_update()
                .filter(reflexo_id=tenant_id)
                .aggregate(m=Max('local_id'))['m']
            )
            next_local = (max_local or 0) + 1
            h = History.objects.create(patient_id=patient_id, reflexo_id=tenant_id, local_id=next_local)
        return JsonResponse({"id": h.id, "reflexo_id": h.reflexo_id}, status=201)
    except IntegrityError:
        # Choque con constraint de único historial activo por paciente
        existing = History.active.filter(patient_id=patient_id).first()
        return JsonResponse({
            "error": "Ya existe un historial activo para este paciente",
            "existing_history_id": existing.id if existing else None
        }, status=409)
    except Exception as e:
        return JsonResponse({"error": "Error al crear el historial"}, status=500)

@csrf_exempt
@api_view(["PUT", "PATCH"])
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def history_update(request, pk):
    """Actualizar historial (PUT/PATCH)"""
    if request.method not in ["PUT", "PATCH"]:
        return HttpResponseNotAllowed(["PUT", "PATCH"])
    
    try:
        h = History.objects.filter(deleted_at__isnull=True).get(pk=pk)
    except History.DoesNotExist:
        return JsonResponse({"error": "No encontrado"}, status=404)
    
    # Manejo de JSON inválido
    try:
        payload = json.loads(request.body.decode())
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)
    
    # Actualizar campos permitidos con casting seguro
    from decimal import Decimal, InvalidOperation
    allowed_fields = ['testimony', 'private_observation', 'observation', 'height', 'weight', 'last_weight', 'menstruation', 'diu_type', 'gestation']

    def _to_decimal(val):
        if val in (None, ""):
            return None
        try:
            return Decimal(str(val))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Formato numérico inválido")

    try:
        for field in allowed_fields:
            if field not in payload:
                continue
            value = payload[field]
            if field in ('height', 'weight', 'last_weight'):
                value = _to_decimal(value)
            elif field in ('testimony', 'menstruation', 'gestation'):
                # Aceptar true/false o strings equivalentes
                if isinstance(value, str):
                    value = value.strip().lower() in ("true", "1", "yes", "si", "sí")
                else:
                    value = bool(value)
            # Asignar valor
            setattr(h, field, value)

        # Guardar y devolver respuesta
        h.save()
        return JsonResponse({
            "status": "updated",
            "id": h.id,
            "data": {
                "testimony": h.testimony,
                "private_observation": h.private_observation,
                "observation": h.observation,
                "height": float(h.height) if h.height is not None else None,
                "weight": float(h.weight) if h.weight is not None else None,
                "last_weight": float(h.last_weight) if h.last_weight is not None else None,
                "menstruation": h.menstruation,
                "diu_type": h.diu_type,
                "gestation": h.gestation,
            }
        })
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        from django.core.exceptions import ValidationError
        if isinstance(e, ValidationError):
            return JsonResponse({"error": e.message_dict if hasattr(e, 'message_dict') else str(e)}, status=400)
        return JsonResponse({"error": "Error al actualizar el historial"}, status=500)

@csrf_exempt
@api_view(["DELETE", "POST"])
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def history_delete(request, pk):
    # Support DELETE as the canonical method; keep POST for backward compatibility
    if request.method not in ["DELETE", "POST"]:
        return HttpResponseNotAllowed(["DELETE", "POST"])
    # Determine deletion mode: default soft delete; hard delete when ?hard=true
    hard_flag = False
    try:
        # Prefer query param for DELETE; for POST also accept JSON body {"hard": true}
        if request.method == "DELETE":
            hard_flag = str(request.GET.get('hard', '')).lower() in ("true", "1", "yes")
        else:
            try:
                body = json.loads(request.body.decode() or '{}')
            except json.JSONDecodeError:
                body = {}
            hard_flag = bool(body.get('hard', False)) or str(request.GET.get('hard', '')).lower() in ("true", "1", "yes")
    except Exception:
        hard_flag = False

    try:
        tenant_id = get_tenant(request.user)
        base = History.objects.filter(deleted_at__isnull=True)
        # Admin global: no restringir por tenant
        if not is_global_admin(request.user):
            # Solo filtrar si el usuario tiene tenant asignado; si no, permitir (sin filtrar)
            if tenant_id is not None:
                base = base.filter(reflexo_id=tenant_id)
        h = base.get(pk=pk)
    except History.DoesNotExist:
        return JsonResponse({"error":"No encontrado"}, status=404)
    
    # Soft delete by default; hard delete when requested
    if hard_flag:
        h.delete()
    else:
        h.soft_delete()
    return JsonResponse({}, status=204)