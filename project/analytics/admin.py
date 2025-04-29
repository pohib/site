from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import SalaryByYear, SalaryByCity, Skill

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