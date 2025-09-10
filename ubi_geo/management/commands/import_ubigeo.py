from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from pathlib import Path
import csv

from ubi_geo.models import Region, Province, District

def getv(row, *cands):
    for k in cands:
        if k in row:
            v = (row.get(k) or "").strip()
            if v != "":
                return v
    return ""

class Command(BaseCommand):
    help = "Importa regiones, provincias y distritos desde CSV (';'). Usa códigos solo para vincular."

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, default="db",
                            help="Carpeta con regions.csv, provinces.csv, districts.csv")
        parser.add_argument("--truncate", action="store_true",
                            help="Borra Region/Province/District antes de importar")
        parser.add_argument(
            "--only",
            nargs="*",
            choices=["regions", "provinces", "districts"],
            help="Importa solo los datasets indicados. Si se omite, importa todos."
        )

    def handle(self, *args, **opt):
        base = Path(opt["path"]).resolve()
        files = {
            "regions": base / "regions.csv",
            "provinces": base / "provinces.csv",
            "districts": base / "districts.csv",
        }
        for name, p in files.items():
            if not p.exists():
                raise CommandError(f"No se encontró {name}: {p}")

        only = set(opt.get("only") or ["regions", "provinces", "districts"])

        if opt["truncate"]:
            self.stdout.write(self.style.WARNING("Truncando tablas seleccionadas…"))
            if "districts" in only:
                District.objects.all().delete()
            if "provinces" in only:
                Province.objects.all().delete()
            if "regions" in only:
                Region.objects.all().delete()

        with transaction.atomic():
            code_to_region = {}
            if "regions" in only:
                # REGIONS (global)
                self.stdout.write("Importando regiones…")
                with files["regions"].open(encoding="utf-8", newline="") as f:
                    r = csv.DictReader(f, delimiter=";")
                    n = u = s = 0
                    for row in r:
                        code = getv(row, "code", "ubigeo_code")
                        name = getv(row, "name", "Nombre")
                        if not name:
                            s += 1; continue
                        try:
                            code_int = int(code) if code else None
                        except ValueError:
                            code_int = None
                        # usar ubigeo_code como clave única y actualizar nombre
                        obj, created = Region.objects.update_or_create(
                            ubigeo_code=code_int,
                            defaults={"name": name}
                        )
                        if code:
                            code_to_region[code] = obj
                        n += int(created); u += int(not created)
                    self.stdout.write(f"Regions: +{n} upd:{u} skip:{s}")
            else:
                # Si no importamos regiones, construir el mapa leyendo la BD por código
                for reg in Region.objects.all().only("id", "ubigeo_code"):
                    if reg.ubigeo_code is not None:
                        code_to_region[str(reg.ubigeo_code)] = reg

            code_to_province = {}
            if "provinces" in only:
                # PROVINCES (global)
                self.stdout.write("Importando provincias…")
                with files["provinces"].open(encoding="utf-8", newline="") as f:
                    r = csv.DictReader(f, delimiter=";")
                    n = u = s = 0
                    seq = 0
                    for row in r:
                        code = getv(row, "code", "ubigeo_code")
                        name = getv(row, "name", "Nombre")
                        region_ref = getv(row, "region_code", "region_id")
                        region = code_to_region.get(region_ref)
                        if not (name and region):
                            s += 1; continue
                        try:
                            code_int = int(code) if code else None
                        except ValueError:
                            code_int = None
                        seq += 1
                        obj, created = Province.objects.update_or_create(
                            ubigeo_code=code_int,
                            defaults={"name": name, "region": region, "sequence": seq}
                        )
                        if code:
                            code_to_province[code] = obj
                        n += int(created); u += int(not created)
                    self.stdout.write(f"Provinces: +{n} upd:{u} skip:{s}")
            else:
                # Si no importamos provincias, construir mapa desde BD
                for prov in Province.objects.select_related("region").only("id", "ubigeo_code"):
                    if prov.ubigeo_code is not None:
                        code_to_province[str(prov.ubigeo_code)] = prov

            if "districts" in only:
                # DISTRICTS (global)
                self.stdout.write("Importando distritos…")
                n = u = s = 0
                seq = 0
                with files["districts"].open(encoding="utf-8", newline="") as f:
                    r = csv.DictReader(f, delimiter=";")
                    for row in r:
                        code = getv(row, "code", "ubigeo_code")
                        name = getv(row, "name", "Nombre")
                        prov_ref = getv(row, "province_code", "province_id")
                        province = code_to_province.get(prov_ref)
                        if not (name and province):
                            s += 1; continue
                        try:
                            code_int = int(code) if code else None
                        except ValueError:
                            code_int = None
                        seq += 1
                        _, created = District.objects.update_or_create(
                            ubigeo_code=code_int,
                            defaults={"name": name, "province": province, "sequence": seq}
                        )
                        n += int(created); u += int(not created)
                self.stdout.write(f"Districts: +{n} upd:{u} skip:{s}")

        self.stdout.write(self.style.SUCCESS("Importación completada ✔"))
