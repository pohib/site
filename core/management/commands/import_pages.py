import os
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Page
from pathlib import Path

class Command(BaseCommand):
    help = 'Импортирует HTML файлы в админку сайта'

    def handle(self, *args, **options):
        templates_dir = Path(settings.BASE_DIR) / 'templates'
        page_mappings = {
            'home.html': 'home',
            'analytics/general_stats.html': 'general-stats',
            'analytics/demand.html': 'demand',
            'analytics/geography.html': 'geography',
            'analytics/skills.html': 'skills',
            'vacancies/latest.html': 'latest'
        }
        
        for page_file, slug in page_mappings.items():
            file_path = templates_dir / page_file
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                Page.objects.update_or_create(
                    slug=slug,
                    defaults={
                        'title': self.get_title(slug),
                        'content': content,
                        'is_html': True
                    }
                )
                self.stdout.write(self.style.SUCCESS(f'Успешно импортировано {page_file}'))
            else:
                self.stdout.write(self.style.WARNING(f'Файл {page_file} не найден'))
    
    def get_title(self, slug):
        titles = {
            'home': 'Главная страница',
            'general-stats': 'Общая статистика',
            'demand': 'Востребованность',
            'geography': 'География',
            'skills': 'Навыки',
            'latest': 'Последние вакансии'
        }
        return titles.get(slug, slug.replace('-', ' ').title())