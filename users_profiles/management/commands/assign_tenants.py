"""
Comando para asignar tenants a usuarios que no los tienen.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from users_profiles.models import User
from reflexo.models import Reflexo


class Command(BaseCommand):
    help = 'Asigna tenants a usuarios que no tienen uno asignado'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué usuarios serían actualizados sin hacer cambios',
        )
        parser.add_argument(
            '--default-tenant',
            type=int,
            help='ID del tenant por defecto para usuarios sin tenant',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        default_tenant_id = options.get('default_tenant')

        # Obtener usuarios sin tenant (excluyendo superusuarios)
        users_without_tenant = User.objects.filter(reflexo_id__isnull=True, is_superuser=False)
        count = users_without_tenant.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ Todos los usuarios ya tienen tenant asignado')
            )
            return

        self.stdout.write(f'📊 Encontrados {count} usuarios sin tenant asignado')

        if dry_run:
            self.stdout.write('\n🔍 MODO DRY-RUN - No se realizarán cambios')
            for user in users_without_tenant:
                self.stdout.write(f'  - Usuario ID {user.id}: {user.email} (Superuser: {user.is_superuser})')
            return

        # Si no se especifica tenant por defecto, mostrar opciones
        if not default_tenant_id:
            tenants = Reflexo.objects.all()
            if not tenants.exists():
                raise CommandError('❌ No hay tenants disponibles. Crea al menos uno.')
            
            self.stdout.write('\n📋 Tenants disponibles:')
            for tenant in tenants:
                self.stdout.write(f'  ID {tenant.id}: {tenant.name}')
            
            raise CommandError(
                '❌ Debes especificar --default-tenant <id> para asignar un tenant por defecto'
            )

        # Verificar que el tenant existe
        try:
            default_tenant = Reflexo.objects.get(id=default_tenant_id)
        except Reflexo.DoesNotExist:
            raise CommandError(f'❌ Tenant con ID {default_tenant_id} no existe')

        # Asignar tenant a usuarios
        with transaction.atomic():
            updated_count = users_without_tenant.update(reflexo_id=default_tenant_id)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Asignado tenant "{default_tenant.name}" a {updated_count} usuarios'
                )
            )

        # Verificar resultado
        remaining = User.objects.filter(reflexo_id__isnull=True).count()
        if remaining == 0:
            self.stdout.write(
                self.style.SUCCESS('🎉 Todos los usuarios ahora tienen tenant asignado')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Aún quedan {remaining} usuarios sin tenant')
            )
