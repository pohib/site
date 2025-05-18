import os
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Page
from pathlib import Path

class Command(BaseCommand):
    help = 'Imports HTML pages from templates directory into Page model'

    def handle(self, *args, **options):
        templates_dir = Path(settings.BASE_DIR) / 'templates'
        
        pages_to_import = [
            'home.html',
            'analytics/general_stats.html',
            'analytics/demand.html',
            'analytics/geography.html',
            'analytics/skills.html',
            'vacancies/latest.html'
        ]
        
        for page_file in pages_to_import:
            file_path = templates_dir / page_file
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                title = page_file.replace('.html', '').replace('_', ' ').title()
                slug = page_file.replace('.html', '')
                
                Page.objects.update_or_create(
                    slug=slug,
                    defaults={
                        'title': title,
                        'content': content,
                        'is_html': True
                    }
                )
                self.stdout.write(self.style.SUCCESS(f'Успешно импортировано {page_file}'))
            else:
                self.stdout.write(self.style.WARNING(f'Файл {page_file} не найден'))