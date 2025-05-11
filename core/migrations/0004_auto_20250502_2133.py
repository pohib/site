from django.db import migrations

def create_homepage(apps, schema_editor):
    HomePage = apps.get_model('core', 'Page')
    HomePage.objects.create(
        title='Главная',
        content='<p>Ваш HTML-контент здесь</p>'
    )
    
class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_page_options_alter_statistic_options_and_more'),
    ]

    operations = [
        migrations.RunPython(create_homepage),
    ]
