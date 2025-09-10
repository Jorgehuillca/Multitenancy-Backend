from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from clinica.models import UserProfile

UserModel = settings.AUTH_USER_MODEL

@receiver(post_save, sender=UserProfile)
def sync_user_reflexo_from_profile(sender, instance: UserProfile, **kwargs):
    """Ensure users_profiles.User.reflexo matches clinica.UserProfile.reflexo.

    This keeps a single source of truth for tenant filtering.
    """
    user = instance.user
    profile_reflexo_id = instance.reflexo_id
    # Only update if different to avoid unnecessary writes
    if getattr(user, 'reflexo_id', None) != profile_reflexo_id:
        # Update the foreign key on the auth user
        user.reflexo_id = profile_reflexo_id
        # Save only the field to avoid touching other columns
        user.save(update_fields=['reflexo'])
