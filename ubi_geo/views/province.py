# -*- coding: utf-8 -*-
from rest_framework.viewsets import ReadOnlyModelViewSet
from ubi_geo.models.province import Province
from ubi_geo.serializers.province import ProvinceSerializer
from architect.utils.tenant import filter_by_tenant_including_global


class ProvinceViewSet(ReadOnlyModelViewSet):
    """
    GET /api/provinces/                 -> lista (se puede filtrar)
    GET /api/provinces/{id}/            -> detalle

    Filtros por querystring:
      - ?region=<id>            -> provincias de esa región
    """
    serializer_class = ProvinceSerializer

    def get_queryset(self):
        qs = Province.objects.select_related("region").filter(deleted_at__isnull=True).order_by("name")
        qs = filter_by_tenant_including_global(qs, self.request.user, field='reflexo')
        region_id = self.request.query_params.get("region")
        if region_id:
            # Aceptar formatos como "{2}" o " 2 "
            rid = str(region_id).strip()
            if rid.startswith("{") and rid.endswith("}"):
                rid = rid[1:-1].strip()
            try:
                rid_int = int(rid)
                qs = qs.filter(region_id=rid_int)
            except (TypeError, ValueError):
                # Si no es un entero válido, no aplicar filtro (evitamos 500)
                pass
        return qs
