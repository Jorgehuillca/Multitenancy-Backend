from django.core.management.base import BaseCommand
from django.db import transaction
from therapists.models.therapist import Therapist

class Command(BaseCommand):
    help = (
        "Assign or renumber Therapist.local_id per tenant (reflexo). "
        "By default renumbers sequentially starting at 1 within each tenant."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--tenant",
            type=int,
            default=None,
            help="Limit to a specific reflexo (tenant) ID.",
        )
        parser.add_argument(
            "--only-missing",
            action="store_true",
            help="Only fill NULL local_id; do not renumber existing values.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without persisting.",
        )

    def handle(self, *args, **options):
        tenant_id = options.get("tenant")
        only_missing = options.get("only_missing", False)
        dry_run = options.get("dry_run", False)

        tenants_qs = (
            Therapist.objects.filter(reflexo__isnull=False)
            .values_list("reflexo_id", flat=True)
            .distinct()
        )
        if tenant_id is not None:
            tenants = [t for t in tenants_qs if t == tenant_id]
            if not tenants:
                self.stdout.write(self.style.WARNING("No therapists found for the specified tenant."))
                return
        else:
            tenants = list(tenants_qs)

        total = 0
        with transaction.atomic():
            for t_id in tenants:
                qs = (
                    Therapist.objects.filter(reflexo_id=t_id, deleted_at__isnull=True)
                    .order_by("created_at", "id")
                    .only("id", "local_id")
                )
                counter = 0
                updated = 0
                for th in qs:
                    if only_missing and th.local_id is not None:
                        continue
                    counter += 1
                    new_local = counter
                    if th.local_id == new_local:
                        continue
                    Therapist.objects.filter(pk=th.pk).update(local_id=new_local)
                    updated += 1
                total += updated
                self.stdout.write(
                    self.style.NOTICE(
                        f"Tenant {t_id}: set/renumbered {updated} therapist local_id(s), final sequence={counter}."
                    )
                )
            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write(self.style.SUCCESS(f"Done. Total therapists updated: {total}. Dry run: {dry_run}"))
