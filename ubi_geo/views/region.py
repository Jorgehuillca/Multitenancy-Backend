# -*- coding: utf-8 -*-
from rest_framework.viewsets import ReadOnlyModelViewSet
from ubi_geo.models.region import Region
from ubi_geo.serializers.region import RegionSerializer
from architect.utils.tenant import filter_by_tenant_including_global

class RegionViewSet(ReadOnlyModelViewSet):
    """
    GET /api/regions/           -> lista todas las regiones
    GET /api/regions/{id}/      -> detalle de una región
    """
    queryset = Region.objects.filter(deleted_at__isnull=True).order_by("name")
    serializer_class = RegionSerializer

    def get_queryset(self):
        base = Region.objects.filter(deleted_at__isnull=True).order_by("name")
        return filter_by_tenant_including_global(base, self.request.user, field='reflexo')
