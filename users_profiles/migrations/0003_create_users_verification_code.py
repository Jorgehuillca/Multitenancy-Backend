# Generated manually to create the users_verification_code table
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('users_profiles', '0002_add_reflexo'),
        ('reflexo', '0001_initial'),
        ('histories_configurations', '0004_alter_paymentstatus_options'),
        ('ubi_geo', '0004_alter_country_options'),
    ]

    operations = [
        migrations.RunSQL(
            sql=r'''
            CREATE TABLE IF NOT EXISTS `users_verification_code` (
              `id` bigint NOT NULL AUTO_INCREMENT,
              `user_id` bigint NOT NULL,
              `reflexo_id` bigint NULL,
              `code` varchar(255) NULL,
              `expires_at` datetime(6) NOT NULL,
              `failed_attempts` int NOT NULL DEFAULT 0,
              `locked_until` datetime(6) NULL,
              `created_at` datetime(6) NOT NULL,
              `updated_at` datetime(6) NOT NULL,
              UNIQUE KEY `users_verification_code_user_id_uniq` (`user_id`),
              PRIMARY KEY (`id`),
              CONSTRAINT `users_verification_code_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
              CONSTRAINT `users_verification_code_reflexo_id_fk` FOREIGN KEY (`reflexo_id`) REFERENCES `reflexo_reflexo` (`id`) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            ''',
            reverse_sql=r"""
            DROP TABLE IF EXISTS `users_verification_code`;
            """,
        ),
    ]
