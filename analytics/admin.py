from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import AnalyticsSettings, SalaryByYear, SalaryByCity, Skill

@admin.register(AnalyticsSettings)
class AnalyticsSettingsAdmin(admin.ModelAdmin):
    list_display = ('skill_count_threshold',)
    
    def has_add_permission(self, request):
        return not AnalyticsSettings.objects.exists()

@admin.register(SalaryByYear)
class SalaryByYearAdmin(admin.ModelAdmin):
    list_display = ('year', 'average_salary', 'vacancy_count', 'profession_average_salary', 'profession_vacancy_count')
    list_editable = ('average_salary', 'vacancy_count', 'profession_average_salary', 'profession_vacancy_count')
    ordering = ('year',)
    search_fields = ('year',)

@admin.register(SalaryByCity)
class SalaryByCityAdmin(admin.ModelAdmin):
    list_display = ('city', 'average_salary', 'vacancy_share', 'is_for_profession')
    list_editable = ('average_salary', 'vacancy_share', 'is_for_profession')
    list_filter = ('is_for_profession',)
    ordering = ('-average_salary',)
    search_fields = ('city',)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'count', 'is_for_profession')
    list_editable = ('count', 'is_for_profession')
    list_filter = ('year', 'is_for_profession')
    ordering = ('-year', '-count')
    search_fields = ('name',)
    
    from django.contrib import admin
from .models import ChartSettings

@admin.register(ChartSettings)
class ChartSettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'chart_type', 'desktop_height', 'mobile_height', 
                'desktop_width', 'mobile_width', 'maintain_aspect_ratio')
    list_editable = ('desktop_height', 'mobile_height', 'desktop_width', 
                    'mobile_width', 'maintain_aspect_ratio')
    fieldsets = (
        (None, {
            'fields': ('name', 'chart_type')
        }),
        ('Размеры для пк версии', {
            'fields': ('desktop_height', 'desktop_width')
        }),
        ('Размеры для мобильных', {
            'fields': ('mobile_height', 'mobile_width')
        }),
        ('Другие настройки', {
            'fields': ('maintain_aspect_ratio',)
        }),
    )