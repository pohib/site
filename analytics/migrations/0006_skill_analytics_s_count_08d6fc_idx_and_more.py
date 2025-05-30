# Generated by Django 5.2 on 2025-05-14 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0005_alter_salarybycity_lat_alter_salarybycity_lon'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='skill',
            index=models.Index(fields=['-count', 'name'], name='analytics_s_count_08d6fc_idx'),
        ),
        migrations.AddIndex(
            model_name='skill',
            index=models.Index(fields=['is_for_profession', '-count'], name='analytics_s_is_for__619d1c_idx'),
        ),
    ]
