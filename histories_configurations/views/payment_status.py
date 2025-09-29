import json
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from ..models import PaymentStatus

@csrf_exempt
def payment_statuses_list(request, pk=None):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    
    # Si se proporciona pk, devolver un estado específico
    if pk is not None:
        try:
            ps = PaymentStatus.objects.get(pk=pk)
            return JsonResponse({
                "id": ps.id,
                "name": ps.name,
                "description": ps.description
            })
        except PaymentStatus.DoesNotExist:
            return JsonResponse({"error": "No encontrado"}, status=404)
    
    # Global: no multitenant constraint for PaymentStatus
    qs = PaymentStatus.objects.all()
    data = [{"id": x.id, "name": x.name, "description": x.description} for x in qs]
    return JsonResponse({"payment_statuses": data})

@csrf_exempt
def payment_status_create(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    try:
        payload = json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    name = (payload.get("name") or "").strip()
    description = (payload.get("description") or None)
    if not name:
        return JsonResponse({"error": "El nombre es requerido"}, status=400)

    ps = PaymentStatus.objects.create(name=name, description=description)
    return JsonResponse({"id": ps.id, "name": ps.name, "description": ps.description}, status=201)

@csrf_exempt
def payment_status_edit(request, pk):
    if request.method not in ["PUT", "PATCH"]:
        return HttpResponseNotAllowed(["PUT", "PATCH"])
    try:
        ps = PaymentStatus.objects.get(pk=pk)
    except PaymentStatus.DoesNotExist:
        return JsonResponse({"error": "No encontrado"}, status=404)

    try:
        payload = json.loads(request.body.decode() or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    if request.method == "PUT":
        # PUT: actualizar todos los campos (name requerido)
        name = (payload.get("name") or "").strip()
        if not name:
            return JsonResponse({"error": "El nombre es requerido"}, status=400)
        ps.name = name
        ps.description = payload.get("description")
    else:
        # PATCH: solo los enviados
        if "name" in payload:
            name = (payload.get("name") or "").strip()
            if not name:
                return JsonResponse({"error": "El nombre es requerido"}, status=400)
            ps.name = name
        if "description" in payload:
            ps.description = payload.get("description")

    ps.save()
    return JsonResponse({"id": ps.id, "name": ps.name, "description": ps.description})

@csrf_exempt
def payment_status_delete(request, pk):
    if request.method != "DELETE":
        return HttpResponseNotAllowed(["DELETE"])
    try:
        ps = PaymentStatus.objects.get(pk=pk)
    except PaymentStatus.DoesNotExist:
        return JsonResponse({"error": "No encontrado"}, status=404)
    # Hard delete global
    ps.delete()
    return JsonResponse({}, status=204)
