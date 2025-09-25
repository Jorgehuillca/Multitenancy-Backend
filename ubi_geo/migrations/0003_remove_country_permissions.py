from django.db import migrations


def remove_country_permissions(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    ct = ContentType.objects.filter(app_label='ubi_geo', model='country').first()
    if not ct:
        return

    Permission.objects.filter(
        content_type=ct,
        codename__in=['add_country', 'change_country', 'delete_country']
    ).delete()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('ubi_geo', '0002_remove_region_country'),
        ('auth', '0001_initial'),  # Ensure auth app is available
        ('contenttypes', '0001_initial'),  # Ensure contenttypes app is available
    ]

    operations = [
        migrations.RunPython(remove_country_permissions, reverse_code=noop),
    ]
