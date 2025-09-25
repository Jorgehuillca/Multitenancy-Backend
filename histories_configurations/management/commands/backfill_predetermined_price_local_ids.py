from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Max
from histories_configurations.models.predetermined_price import PredeterminedPrice

class Command(BaseCommand):
    help = (
        "Asigna o reenumera local_id por empresa (reflexo) para PredeterminedPrice.\n"
        "Por defecto numera secuencialmente iniciando en 1 dentro de cada tenant."
    )

    def add_arguments(self, parser):
        parser.add_argument("--tenant", type=int, default=None, help="Limitar a un reflexo específico (ID).")
        parser.add_argument("--only-missing", action="store_true", help="Solo llenar local_id NULL; no renumerar existentes.")
        parser.add_argument("--dry-run", action="store_true", help="Mostrar cambios sin persistir.")

    def handle(self, *args, **opts):
        tenant = opts.get("tenant")
        only_missing = opts.get("only_missing", False)
        dry = opts.get("dry_run", False)

        tenants_qs = (
            PredeterminedPrice.objects.filter(reflexo__isnull=False)
            .values_list("reflexo_id", flat=True).distinct()
        )
        if tenant is not None:
            tenants = [t for t in tenants_qs if t == tenant]
            if not tenants:
                self.stdout.write(self.style.WARNING("No hay precios predeterminados para ese tenant."))
                return
        else:
            tenants = list(tenants_qs)

        total = 0
        with transaction.atomic():
            for t_id in tenants:
                qs = PredeterminedPrice.objects.filter(reflexo_id=t_id, deleted_at__isnull=True).order_by("created_at", "id")
                counter = 0
                updated = 0
                for item in qs.select_for_update():
                    if only_missing and item.local_id is not None:
                        continue
                    counter += 1
                    new_local = counter
                    if item.local_id == new_local:
                        continue
                    PredeterminedPrice.objects.filter(pk=item.pk).update(local_id=new_local)
                    updated += 1
                total += updated
                self.stdout.write(self.style.NOTICE(f"Tenant {t_id}: actualizados {updated}, secuencia final={counter}"))
            if dry:
                transaction.set_rollback(True)
        self.stdout.write(self.style.SUCCESS(f"Listo. Total actualizados: {total}. Dry run: {dry}"))
