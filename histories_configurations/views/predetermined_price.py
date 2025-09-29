import json
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from ..models.predetermined_price import PredeterminedPrice
from architect.utils.tenant import get_tenant, filter_by_tenant, is_global_admin

@csrf_exempt
@api_view(["GET"])
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def predetermined_prices_list(request, pk=None):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])

    # Si se proporciona pk, devolver un precio específico
    if pk is not None:
        try:
            base = PredeterminedPrice.objects.filter(deleted_at__isnull=True)
            if not is_global_admin(request.user):
                base = filter_by_tenant(base, request.user, field='reflexo')
            p = base.get(pk=pk)
            return JsonResponse({
                "id": p.id,
                "name": p.name,
                "price": str(p.price),
                "reflexo_id": p.reflexo_id,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None
            })
        except PredeterminedPrice.DoesNotExist:
            return JsonResponse({"error": "No encontrado"}, status=404)

    # Aislamiento por tenant (admins globales ven todo)
    qs = PredeterminedPrice.objects.filter(deleted_at__isnull=True)
    try:
        if not is_global_admin(request.user):
            qs = filter_by_tenant(qs, request.user, field='reflexo')
    except Exception:
        qs = filter_by_tenant(qs, request.user, field='reflexo')

    data = [{
        "id": p.id,
        "name": p.name,
        "price": str(p.price)
    } for p in qs]
    return JsonResponse({"predetermined_prices": data})


@csrf_exempt
@api_view(["POST"])
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def predetermined_price_create(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    try:
        payload = json.loads(request.body.decode() or '{}')
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    name = payload.get("name")
    price = payload.get("price")
    if not name or price is None:
        return JsonResponse({"error": "Campos obligatorios faltantes"}, status=400)

    # Determinar tenant según rol
    if is_global_admin(request.user):
        tenant_id = payload.get('reflexo_id') or payload.get('reflexo')
        if tenant_id is None:
            return JsonResponse({"error": "Admin debe especificar reflexo_id"}, status=400)
        try:
            tenant_id = int(tenant_id)
        except (TypeError, ValueError):
            return JsonResponse({"error": "reflexo_id inválido"}, status=400)
    else:
        tenant_id = get_tenant(request.user)
        if tenant_id is None:
            return JsonResponse({"error": "Usuario sin empresa asignada"}, status=403)

    p = PredeterminedPrice.objects.create(name=name, price=price, reflexo_id=tenant_id)
    return JsonResponse({"id": p.id, "reflexo_id": tenant_id}, status=201)


@csrf_exempt
@api_view(["PUT", "PATCH", "POST"])
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def predetermined_price_update(request, pk):
    if request.method not in ["PUT", "PATCH", "POST"]:
        return HttpResponseNotAllowed(["PUT", "PATCH", "POST"])

    try:
        payload = json.loads(request.body.decode() or '{}')
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    try:
        base = PredeterminedPrice.objects.filter(deleted_at__isnull=True)
        if not is_global_admin(request.user):
            base = filter_by_tenant(base, request.user, field='reflexo')
        p = base.get(pk=pk)
    except PredeterminedPrice.DoesNotExist:
        return JsonResponse({"error": "No encontrado"}, status=404)
    
    name = payload.get("name")
    price = payload.get("price")

    # Para PUT, actualizar todos los campos; para PATCH/POST, solo los proporcionados
    if request.method == "PUT":
        if name is not None:
            p.name = name
        if price is not None:
            p.price = price
    else:  # PATCH o POST
        if name is not None:
            p.name = name
        if price is not None:
            p.price = price
    
    p.save()
    return JsonResponse({
        "id": p.id,
        "name": p.name,
        "price": str(p.price)
    })


@csrf_exempt
@api_view(["DELETE", "POST"])
@authentication_classes([JWTAuthentication, SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def predetermined_price_delete(request, pk):
    if request.method not in ["DELETE", "POST"]:
        return HttpResponseNotAllowed(["DELETE", "POST"])

    # Alcance por tenant (si aplica); eliminar definitivamente
    base = PredeterminedPrice.objects.all()
    if not is_global_admin(request.user):
        base = filter_by_tenant(base, request.user, field='reflexo')
    try:
        p = base.get(pk=pk)
    except PredeterminedPrice.DoesNotExist:
        return JsonResponse({"error": "No encontrado"}, status=404)

    p.delete()  # Hard delete: desaparece de Admin y de la BD
    return JsonResponse({}, status=204)
