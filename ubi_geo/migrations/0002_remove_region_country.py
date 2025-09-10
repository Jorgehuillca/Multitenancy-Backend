from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("ubi_geo", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="region",
            name="country",
        ),
    ]
