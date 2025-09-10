from django.db import migrations, connection


def add_missing_columns(apps, schema_editor):
    """Add columns only if they don't exist (works on MySQL < 8.0)."""
    db_name = connection.settings_dict.get("NAME")
    with connection.cursor() as cursor:
        # Check is_used
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA=%s AND TABLE_NAME='users_verification_code' AND COLUMN_NAME='is_used'
            """,
            [db_name],
        )
        (exists_is_used,) = cursor.fetchone()
        if not exists_is_used:
            cursor.execute(
                """
                ALTER TABLE `users_verification_code`
                ADD COLUMN `is_used` TINYINT(1) NOT NULL DEFAULT 0
                """
            )

        # Check verification_type
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA=%s AND TABLE_NAME='users_verification_code' AND COLUMN_NAME='verification_type'
            """,
            [db_name],
        )
        (exists_vtype,) = cursor.fetchone()
        if not exists_vtype:
            cursor.execute(
                """
                ALTER TABLE `users_verification_code`
                ADD COLUMN `verification_type` VARCHAR(50) NOT NULL DEFAULT 'password_change'
                """
            )


def noop_reverse(apps, schema_editor):
    # Keep columns; no reverse action required
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("users_profiles", "0007_userverificationcode_reflexo_and_more"),
    ]

    operations = [
        migrations.RunPython(add_missing_columns, noop_reverse),
    ]
