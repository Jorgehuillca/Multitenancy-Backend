import json
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from ..models.payment_type import PaymentType
from architect.utils.tenant import get_tenant

@csrf_exempt
def payment_types_list(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    # Global: no filtrar por tenant
    qs = PaymentType.objects.filter(deleted_at__isnull=True)
    data = [{"id": x.id, "name": x.name} for x in qs]
    return JsonResponse({"payment_types": data})

@csrf_exempt
def payment_type_create(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    payload = json.loads(request.body.decode() or "{}")
    name = (payload.get("name") or "").strip()
    if not name:
        return JsonResponse({"error": "El nombre es requerido"}, status=400)
    # Global: PaymentType no es multitenant
    pt = PaymentType.objects.create(name=name)
    return JsonResponse({"id": pt.id, "name": pt.name}, status=201)

@csrf_exempt
def payment_type_delete(request, pk):
    if request.method != "DELETE":
        return HttpResponseNotAllowed(["DELETE"])
    try:
        # Global hard delete: no filtrar por tenant
        pt = PaymentType.objects.get(pk=pk)
    except PaymentType.DoesNotExist:
        return JsonResponse({"error": "No encontrado"}, status=404)
    pt.delete()
    return JsonResponse({}, status=204)

@csrf_exempt
def payment_type_edit(request, pk):
    if request.method not in ["PUT", "PATCH"]:
        return HttpResponseNotAllowed(["PUT", "PATCH"])

    try:
        # Global: no filtrar por tenant
        pt = PaymentType.objects.get(pk=pk, deleted_at__isnull=True)
    except PaymentType.DoesNotExist:
        return JsonResponse({"error": "No encontrado"}, status=404)

    payload = json.loads(request.body.decode() or "{}")
    
    # Para PUT, actualizar todos los campos; para PATCH, solo los proporcionados
    if request.method == "PUT":
        pt.name = payload.get("name", pt.name)
    else:  # PATCH
        if "name" in payload:
            pt.name = payload["name"]

    pt.save()
    return JsonResponse({
        "id": pt.id,
        "name": pt.name
    }, status=200)