# ubi_geo/signals.py
from django.apps import apps
from django.core.management import call_command
from django.db.models.signals import post_migrate
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)


@receiver(post_migrate)
def ensure_default_ubigeo(sender, app_config=None, **kwargs):
    """After migrations, ensure Regions/Provinces/Districts are preloaded from db/*.csv.

    - Only triggers for the ubi_geo app.
    - Skips if data already exists to avoid duplicates.
    - Uses the existing management command: `import_ubigeo`.
    """
    try:
        # Limit execution to ubi_geo app migrations only
        if app_config is None or app_config.label != 'ubi_geo':
            return

        Region = apps.get_model('ubi_geo', 'Region')
        Province = apps.get_model('ubi_geo', 'Province')
        District = apps.get_model('ubi_geo', 'District')

        has_regions = Region.objects.exists()
        has_provinces = Province.objects.exists()
        has_districts = District.objects.exists()

        if has_regions and has_provinces and has_districts:
            logger.info("UbiGeo seed: data already present. Skipping import.")
            return

        logger.info("UbiGeo seed: importing regions/provinces/districts from db/…")
        # Use default path 'db' (relative to project root)
        call_command('import_ubigeo', path='db')
        logger.info("UbiGeo seed: import completed.")
    except Exception as e:
        # Do not break application startup due to seed issues
        logger.exception("UbiGeo seed: import failed: %s", e)
