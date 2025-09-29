# -*- coding: utf-8 -*-
from rest_framework.viewsets import ReadOnlyModelViewSet
from ubi_geo.models.region import Region
from ubi_geo.serializers.region import RegionSerializer

class RegionViewSet(ReadOnlyModelViewSet):
    """
    GET /api/locations/regions/           -> lista todas las regiones
    GET /api/locations/regions/{id}/      -> detalle de una región
    """
    queryset = Region.objects.filter(deleted_at__isnull=True).order_by("name")
    serializer_class = RegionSerializer
