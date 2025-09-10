from django.core.management.base import BaseCommand, CommandError
from users_profiles.models import User
from reflexo.models import Reflexo

class Command(BaseCommand):
    help = "Lists users and their tenant (reflexo). Optionally set a tenant for a specific user by id or email."

    def add_arguments(self, parser):
        parser.add_argument('--set-user-id', type=int, help='User id to set tenant for')
        parser.add_argument('--set-user-email', type=str, help='User email to set tenant for')
        parser.add_argument('--tenant', type=int, help='Reflexo id to assign to the user')

    def handle(self, *args, **options):
        set_user_id = options.get('set_user_id')
        set_user_email = options.get('set_user_email')
        tenant_id = options.get('tenant')

        users = list(User.objects.values('id','email','user_name','reflexo_id').order_by('id'))
        self.stdout.write('USERS:')
        for u in users:
            self.stdout.write(str(u))

        if set_user_id or set_user_email:
            if not tenant_id:
                raise CommandError('Provide --tenant <ID> when using --set-user-id/--set-user-email')
            try:
                reflexo = Reflexo.objects.get(pk=tenant_id)
            except Reflexo.DoesNotExist:
                raise CommandError(f'Reflexo with id {tenant_id} does not exist')
            if set_user_id:
                user = User.objects.get(pk=set_user_id)
            else:
                user = User.objects.get(email=set_user_email)
            user.reflexo_id = reflexo.id
            user.save(update_fields=['reflexo'])
            self.stdout.write(self.style.SUCCESS(f'User {user.id} updated to reflexo {reflexo.id}'))
