# Generated by Django 5.2 on 2025-04-28 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Vacancy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('skills', models.TextField()),
                ('company', models.CharField(max_length=200)),
                ('salary', models.CharField(max_length=100)),
                ('region', models.CharField(max_length=100)),
                ('published_at', models.DateTimeField()),
                ('url', models.URLField()),
            ],
            options={
                'verbose_name_plural': 'Vacancies',
                'ordering': ['-published_at'],
            },
        ),
    ]
