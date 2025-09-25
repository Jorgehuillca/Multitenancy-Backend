from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import datetime, time
from appointments_status.models.appointment import Appointment

class Command(BaseCommand):
    help = (
        "Fix appointments with missing appointment_date or hour. "
        "- If appointment_date has time and hour is NULL, set hour = appointment_date.time().\n"
        "- If appointment_date is NULL but initial_date and hour exist, set appointment_date = combine(initial_date, hour).\n"
    )

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Do not persist changes.")
        parser.add_argument("--tenant", type=int, default=None, help="Limit to a specific reflexo (tenant) ID.")

    def handle(self, *args, **opts):
        dry = opts.get("dry_run", False)
        tenant = opts.get("tenant")

        qs = Appointment.objects.all()
        if tenant is not None:
            qs = qs.filter(reflexo_id=tenant)

        to_fix = qs.filter(models.Q(appointment_date__isnull=True) | models.Q(hour__isnull=True))
        total = to_fix.count()
        fixed = 0

        with transaction.atomic():
            for ap in to_fix.select_for_update():
                changed = False
                if ap.appointment_date and ap.hour is None:
                    try:
                        ap.hour = ap.appointment_date.time()
                        changed = True
                    except Exception:
                        pass
                if ap.appointment_date is None and ap.initial_date and ap.hour:
                    try:
                        ap.appointment_date = datetime.combine(ap.initial_date, ap.hour)
                        changed = True
                    except Exception:
                        pass
                if changed:
                    ap.save(update_fields=["appointment_date", "hour", "updated_at"])
                    fixed += 1
            if dry:
                transaction.set_rollback(True)
        self.stdout.write(self.style.SUCCESS(f"Checked {total} appointments, fixed {fixed}. Dry run: {dry}"))
