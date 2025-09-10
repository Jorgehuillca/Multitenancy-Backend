# ubi_geo/apps.py
from django.apps import AppConfig

class UbiGeoConfig(AppConfig):   # <-- SIN guion bajo
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ubi_geo'

    def ready(self):
        # Registrar señales (post_migrate) para autoseed de ubigeo
        try:
            import ubi_geo.signals  # noqa: F401
        except Exception:
            # No impedir el arranque si las señales fallan al importar
            pass
