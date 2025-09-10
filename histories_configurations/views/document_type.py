import json
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from ..models.document_type import DocumentType
from architect.utils.tenant import get_tenant, is_global_admin

@csrf_exempt
def document_types_list(request):
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    # Global: no filtrar por tenant
    qs = DocumentType.objects.filter(deleted_at__isnull=True)
    data = [{"id": x.id, "name": x.name} for x in qs]
    return JsonResponse({"document_types": data})

@csrf_exempt
def document_type_create(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    payload = json.loads(request.body.decode() or "{}")
    name = (payload.get("name") or "").strip()
    if not name:
        return JsonResponse({"error": "El nombre es requerido"}, status=400)
    # Global: DocumentType no es multitenant
    dt = DocumentType.objects.create(name=name)
    return JsonResponse({"id": dt.id, "name": dt.name}, status=201)


@csrf_exempt
def document_type_delete(request, pk):
    if request.method != "DELETE":
        return HttpResponseNotAllowed(["DELETE"])
    try:
        # Global hard delete: no filtrar por tenant ni estado
        dt = DocumentType.objects.get(pk=pk)
    except DocumentType.DoesNotExist:
        return JsonResponse({"error": "No encontrado"}, status=404)
    dt.delete()
    return JsonResponse({}, status=204)

@csrf_exempt
def document_type_edit(request, pk):
    if request.method not in ["PUT", "PATCH"]:
        return HttpResponseNotAllowed(["PUT", "PATCH"])

    try:
        dt = DocumentType.objects.get(pk=pk, deleted_at__isnull=True)
    except DocumentType.DoesNotExist:
        return JsonResponse({"error": "No encontrado"}, status=404)
    
    payload = json.loads(request.body.decode() or "{}")
    
    # Para PUT, actualizar todos los campos; para PATCH, solo los proporcionados
    if request.method == "PUT":
        dt.name = payload.get("name", dt.name)
    else:  # PATCH
        if "name" in payload:
            dt.name = payload["name"]

    dt.save()
    return JsonResponse({
        "id": dt.id,
        "name": dt.name
    }, status=200)
