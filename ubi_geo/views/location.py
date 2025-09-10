from rest_framework.viewsets import ReadOnlyModelViewSet
from ubi_geo.models.region import Region
from ubi_geo.models.province import Province
from ubi_geo.models.district import District
from ubi_geo.serializers.region import RegionSerializer
from ubi_geo.serializers.province import ProvinceSerializer
from ubi_geo.serializers.district import DistrictSerializer
from architect.utils.tenant import filter_by_tenant

class RegionViewSet(ReadOnlyModelViewSet):
    queryset = Region.objects.filter(deleted_at__isnull=True).order_by("name")
    serializer_class = RegionSerializer

    def get_queryset(self):
        base = Region.objects.filter(deleted_at__isnull=True).order_by("name")
        return filter_by_tenant(base, self.request.user, field='reflexo')

class ProvinceViewSet(ReadOnlyModelViewSet):
    serializer_class = ProvinceSerializer

    def get_queryset(self):
        qs = Province.objects.select_related("region").filter(deleted_at__isnull=True).order_by("name")
        qs = filter_by_tenant(qs, self.request.user, field='reflexo')
        region_id = self.request.query_params.get("region")
        if region_id:
            qs = qs.filter(region_id=region_id)
        return qs

class DistrictViewSet(ReadOnlyModelViewSet):
    serializer_class = DistrictSerializer

    def get_queryset(self):
        qs = District.objects.select_related("province", "province__region").filter(deleted_at__isnull=True).order_by("name")
        qs = filter_by_tenant(qs, self.request.user, field='reflexo')
        province_id = self.request.query_params.get("province")
        if province_id:
            qs = qs.filter(province_id=province_id)
        return qs
