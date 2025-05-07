from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Page, Statistic

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    
    class Meta:
        verbose_name = _('страницу')
        verbose_name_plural = _('Страницы')

@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ('title', 'page', 'order')
    list_editable = ('order',)
    list_filter = ('page',)
    
    class Meta:
        verbose_name = _('статистику')
        verbose_name_plural = _('Статистика')