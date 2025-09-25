from django.core.management.base import BaseCommand
from django.db import transaction
from appointments_status.models import Ticket

class Command(BaseCommand):
    help = "Backfill ticket.reflexo from related appointment when missing (NULL)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Do not write changes, only show what would be updated",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limit the number of records to process (0 = no limit)",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        limit = options.get("limit", 0)

        qs = Ticket.objects.filter(reflexo__isnull=True, appointment__isnull=False)
        total = qs.count()
        if limit and limit > 0:
            qs = qs[:limit]

        self.stdout.write(self.style.NOTICE(f"Found {total} tickets with NULL reflexo_id (processing {qs.count()} records)..."))

        updated = 0
        with transaction.atomic():
            for t in qs.select_related("appointment"):
                tenant = getattr(t.appointment, "reflexo", None)
                if tenant is None:
                    continue
                t.reflexo = tenant
                if not dry_run:
                    t.save(update_fields=["reflexo", "updated_at"])  # updated_at if model has it
                updated += 1
            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write(self.style.SUCCESS(f"Done. Updated {updated} ticket(s). Dry run: {dry_run}"))
