import csv
from pathlib import Path
from typing import Tuple

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from patients_diagnoses.models.diagnosis import Diagnosis


class Command(BaseCommand):
    help = (
        "Importa diagnósticos globales desde un CSV con encabezado 'code;name' "
        "ubicado por defecto en db/diagnoses.csv. Upsert por code (crea o actualiza)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            dest="path",
            default="db/diagnoses.csv",
            help="Ruta al CSV (por defecto: db/diagnoses.csv)",
        )
        parser.add_argument(
            "--delimiter",
            dest="delimiter",
            default=";",
            help="Delimitador del CSV (por defecto: ';')",
        )
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Vacía la tabla antes de importar (hard reset).",
        )

    def handle(self, *args, **options):
        path = Path(options["path"]).resolve()
        delimiter = options["delimiter"]
        truncate = options["truncate"]

        if not path.exists():
            raise CommandError(f"No se encontró el archivo: {path}")

        self.stdout.write(self.style.NOTICE(f"Leyendo {path} ..."))

        rows: list[Tuple[str, str]] = []
        with path.open("r", encoding="utf-8", newline="") as f:
            # Primera pasada para limpiar BOM y normalizar encabezados
            _peek = f.readline()
            if not _peek:
                raise CommandError("El archivo está vacío")
            f.seek(0)
            reader = csv.reader(f, delimiter=delimiter)
            raw_header = next(reader)
            norm_header = [h.strip().lstrip('\ufeff').lower() for h in raw_header]
            # Validar columnas requeridas
            if not {"code", "name"}.issubset(set(norm_header)):
                raise CommandError(
                    f"Encabezados inválidos. Se esperaba al menos: code{delimiter}name; encontrados: {raw_header}"
                )
            # Construir un DictReader con los encabezados normalizados
            f.seek(0)
            reader = csv.DictReader(f, fieldnames=norm_header, delimiter=delimiter)
            next(reader)  # saltar la fila de encabezados original
            for i, row in enumerate(reader, start=2):  # start=2 por el header
                code = (row.get("code") or "").strip()
                name = (row.get("name") or "").strip()
                if not code or not name:
                    self.stdout.write(self.style.WARNING(f"Fila {i} omitida (code/name vacío)"))
                    continue
                rows.append((code, name))

        if not rows:
            self.stdout.write(self.style.WARNING("No hay filas válidas para importar."))
            return

        created = 0
        updated = 0

        with transaction.atomic():
            if truncate:
                Diagnosis.all_objects.all().delete()
                self.stdout.write(self.style.WARNING("Tabla 'diagnoses' vaciada (truncate)."))

            # Mapear existentes por code
            codes = [c for c, _ in rows]
            existing = {d.code: d for d in Diagnosis.all_objects.filter(code__in=codes)}

            to_create: list[Diagnosis] = []
            to_update: list[Diagnosis] = []

            for code, name in rows:
                if code in existing:
                    diag = existing[code]
                    # Asegurar globalidad y valores actuales
                    changed = False
                    if diag.name != name:
                        diag.name = name
                        changed = True
                    if diag.reflexo_id is not None:
                        diag.reflexo_id = None
                        changed = True
                    if diag.deleted_at is not None:
                        diag.deleted_at = None
                        changed = True
                    if changed:
                        to_update.append(diag)
                else:
                    to_create.append(
                        Diagnosis(code=code, name=name, reflexo=None, deleted_at=None)
                    )

            if to_create:
                Diagnosis.objects.bulk_create(to_create, batch_size=2000)
                created = len(to_create)
            if to_update:
                Diagnosis.all_objects.bulk_update(
                    to_update, ["name", "reflexo_id", "deleted_at"], batch_size=2000
                )
                updated = len(to_update)

        self.stdout.write(
            self.style.SUCCESS(
                f"Importación completada: creados={created}, actualizados={updated}, total_leído={len(rows)}"
            )
        )
