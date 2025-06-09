from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Очищает весь кэш Django'

    def handle(self, *args, **options):
        cache.clear()
        
        if hasattr(settings, 'CACHES'):
            for alias in settings.CACHES:
                if settings.CACHES[alias]['BACKEND'] == 'django.core.cache.backends.filebased.FileBasedCache':
                    cache_dir = settings.CACHES[alias]['LOCATION']
                    if os.path.exists(cache_dir):
                        for filename in os.listdir(cache_dir):
                            file_path = os.path.join(cache_dir, filename)
                            try:
                                if os.path.isfile(file_path):
                                    os.unlink(file_path)
                            except Exception as e:
                                print(f"Ошибка при удалении {file_path}: {e}")
        
        self.stdout.write(self.style.SUCCESS('Кэш успешно очищен'))