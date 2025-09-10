from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from clinica.models import UserProfile
from reflexo.models import Reflexo

class Command(BaseCommand):
    help = "Lists each user with existence of Clinica.UserProfile and its reflexo_id/name"

    def handle(self, *args, **options):
        User = get_user_model()
        users = User.objects.all().order_by('id')
        self.stdout.write('USERS WITH PROFILE INFO:')
        for u in users:
            try:
                p = UserProfile.objects.get(user=u)
                ref_id = p.reflexo_id
                ref_name = None
                if ref_id is not None:
                    ref_name = Reflexo.objects.filter(pk=ref_id).values_list('name', flat=True).first()
                self.stdout.write(str({
                    'user_id': u.id,
                    'email': u.email,
                    'user_reflexo_id': u.reflexo_id,
                    'profile_exists': True,
                    'profile_reflexo_id': ref_id,
                    'profile_reflexo_name': ref_name,
                }))
            except UserProfile.DoesNotExist:
                self.stdout.write(str({
                    'user_id': u.id,
                    'email': u.email,
                    'user_reflexo_id': u.reflexo_id,
                    'profile_exists': False,
                    'profile_reflexo_id': None,
                    'profile_reflexo_name': None,
                }))
