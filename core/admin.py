from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Page, Statistic

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'show_in_menu', 'menu_icon')
    list_editable = ('show_in_menu', 'menu_icon')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)
    list_filter = ('is_html',)
    readonly_fields = ('is_html',)
    actions = ['import_html_pages']
    
    @admin.action(description='Импортировать HTML страницы')
    def import_html_pages(self, request, queryset):
        from django.core.management import call_command
        call_command('import_pages')
        self.message_user(request, "HTML страницы успешно импортированы")
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