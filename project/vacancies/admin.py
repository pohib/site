from django.contrib import admin
from .models import Vacancy

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'region', 'published_at')
    list_filter = ('region', 'published_at')
    search_fields = ('title', 'company', 'skills')
    date_hierarchy = 'published_at'