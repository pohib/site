from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Vacancy

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'region', 'published_at', 'salary')
    list_filter = ('region', 'published_at', 'company')
    search_fields = ('title', 'company', 'skills', 'description')
    date_hierarchy = 'published_at'
    list_per_page = 20
    ordering = ('-published_at',)