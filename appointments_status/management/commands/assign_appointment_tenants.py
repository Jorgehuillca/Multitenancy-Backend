"""
Comando para asignar tenants a citas que no los tienen.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from appointments_status.models import Appointment
from patients_diagnoses.models import Patient


class Command(BaseCommand):
    help = 'Asigna tenants a citas que no tienen uno asignado basándose en el paciente'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué citas serían actualizadas sin hacer cambios',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Obtener citas sin tenant
        appointments_without_tenant = Appointment.objects.filter(reflexo_id__isnull=True)
        count = appointments_without_tenant.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ Todas las citas ya tienen tenant asignado')
            )
            return

        self.stdout.write(f'📊 Encontradas {count} citas sin tenant asignado')

        if dry_run:
            self.stdout.write('\n🔍 MODO DRY-RUN - No se realizarán cambios')
            for appointment in appointments_without_tenant:
                patient_tenant = appointment.patient.reflexo_id if appointment.patient else None
                self.stdout.write(
                    f'  - Cita ID {appointment.id}: Paciente {appointment.patient.name if appointment.patient else "N/A"} '
                    f'(Tenant del paciente: {patient_tenant})'
                )
            return

        # Asignar tenant basándose en el paciente
        updated_count = 0
        with transaction.atomic():
            for appointment in appointments_without_tenant:
                if appointment.patient and appointment.patient.reflexo_id:
                    appointment.reflexo_id = appointment.patient.reflexo_id
                    appointment.save(update_fields=['reflexo_id'])
                    updated_count += 1
                    self.stdout.write(
                        f'✅ Cita ID {appointment.id} asignada al tenant {appointment.patient.reflexo_id} '
                        f'(basándose en paciente {appointment.patient.name})'
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️  Cita ID {appointment.id} no se puede asignar - paciente sin tenant'
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(f'🎉 Actualizadas {updated_count} citas con tenant asignado')
        )

        # Verificar resultado
        remaining = Appointment.objects.filter(reflexo_id__isnull=True).count()
        if remaining == 0:
            self.stdout.write(
                self.style.SUCCESS('🎉 Todas las citas ahora tienen tenant asignado')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Aún quedan {remaining} citas sin tenant')
            )
