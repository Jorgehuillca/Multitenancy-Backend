from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from clinica.models import UserProfile

class Command(BaseCommand):
    help = "Synchronize users_profiles.User.reflexo from clinica.UserProfile.reflexo for all users."

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Only show what would change')

    def handle(self, *args, **options):
        User = get_user_model()
        dry = options['dry_run']
        updated = 0
        total = 0
        for u in User.objects.all().order_by('id'):
            total += 1
            try:
                p = UserProfile.objects.get(user=u)
            except UserProfile.DoesNotExist:
                self.stdout.write(f"User {u.id} {u.email}: no profile")
                continue
            prof_ref = p.reflexo_id
            if u.reflexo_id != prof_ref:
                self.stdout.write(f"User {u.id} {u.email}: {u.reflexo_id} -> {prof_ref}")
                if not dry:
                    u.reflexo_id = prof_ref
                    u.save(update_fields=['reflexo'])
                    updated += 1
            else:
                self.stdout.write(f"User {u.id} {u.email}: already {u.reflexo_id}")
        self.stdout.write(self.style.SUCCESS(f"Processed {total} users, updated {updated}"))
