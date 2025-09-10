from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from patients_diagnoses.models.patient import Patient
from reflexo.models import Reflexo


class Command(BaseCommand):
    help = "Assigns a tenant (reflexo) to patients with NULL tenant. Usage: manage.py backfill_patient_tenant --tenant <ID>"

    def add_arguments(self, parser):
        parser.add_argument('--tenant', type=int, required=True, help='ID of Reflexo (tenant) to assign to orphan patients')
        parser.add_argument('--dry-run', action='store_true', help='Only show what would change, do not write')

    def handle(self, *args, **options):
        tenant_id = options['tenant']
        dry_run = options['dry_run']

        try:
            tenant = Reflexo.objects.get(pk=tenant_id)
        except Reflexo.DoesNotExist:
            raise CommandError(f"Reflexo with id {tenant_id} does not exist")

        qs = Patient.objects.filter(reflexo__isnull=True)
        count = qs.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No patients with NULL tenant were found.'))
            return

        self.stdout.write(self.style.WARNING(f"Found {count} patients with NULL tenant. Target tenant: {tenant} (id={tenant.id})"))

        if dry_run:
            for p in qs.only('id', 'name')[:50]:
                self.stdout.write(f"Would update Patient(id={p.id}, name={p.name}) -> reflexo_id={tenant.id}")
            self.stdout.write(self.style.SUCCESS('Dry run complete. No changes written.'))
            return

        with transaction.atomic():
            updated = qs.update(reflexo_id=tenant.id)
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} patients to tenant id {tenant.id}"))
