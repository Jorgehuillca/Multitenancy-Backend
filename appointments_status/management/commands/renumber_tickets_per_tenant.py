from django.core.management.base import BaseCommand
from django.db import transaction
from appointments_status.models import Ticket

class Command(BaseCommand):
    help = "Renumber tickets per tenant (reflexo) to TKT-001, TKT-002, ... in created_at order."

    def add_arguments(self, parser):
        parser.add_argument(
            "--tenant",
            type=int,
            default=None,
            help="Reflexo (tenant) ID to limit the renumbering. If omitted, process all tenants.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only show what would change; do not persist.",
        )

    def handle(self, *args, **options):
        tenant_id = options.get("tenant")
        dry_run = options.get("dry_run", False)

        tenants = (
            Ticket.objects.filter(reflexo__isnull=False)
            .values_list("reflexo_id", flat=True)
            .distinct()
        )
        if tenant_id is not None:
            tenants = [t for t in tenants if t == tenant_id]
            if not tenants:
                self.stdout.write(self.style.WARNING("No tickets found for the specified tenant."))
                return

        total_updated = 0
        with transaction.atomic():
            for t_id in tenants:
                # Order by creation to preserve chronology per tenant
                qs = (
                    Ticket.objects.filter(reflexo_id=t_id)
                    .order_by("created_at", "id")
                    .only("id", "ticket_number")
                )
                counter = 0
                updated_for_tenant = 0
                for ticket in qs:
                    counter += 1
                    new_number = f"TKT-{counter:03d}"
                    if ticket.ticket_number == new_number:
                        continue
                    # Ensure no clash: check if any other ticket within this tenant has this number already
                    clash = (
                        Ticket.objects.filter(reflexo_id=t_id, ticket_number=new_number)
                        .exclude(pk=ticket.pk)
                        .exists()
                    )
                    if clash:
                        # This should not happen if we process sequentially, but guard anyway
                        self.stdout.write(
                            self.style.ERROR(
                                f"Skipping ticket {ticket.id}: target number {new_number} already exists for tenant {t_id}."
                            )
                        )
                        continue
                    Ticket.objects.filter(pk=ticket.pk).update(ticket_number=new_number)
                    updated_for_tenant += 1
                total_updated += updated_for_tenant
                self.stdout.write(
                    self.style.NOTICE(
                        f"Tenant {t_id}: renumbered {updated_for_tenant} tickets (sequence length={counter})."
                    )
                )
            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write(self.style.SUCCESS(f"Done. Total tickets renumbered: {total_updated}. Dry run: {dry_run}"))
