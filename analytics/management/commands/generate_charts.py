from django.core.management.base import BaseCommand
from generate_analytics import generate_all_charts

class Command(BaseCommand):
    help = 'Generate analytics charts'

    def handle(self, *args, **options):
        generate_all_charts()
        self.stdout.write(self.style.SUCCESS('Charts generated successfully'))