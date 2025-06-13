from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Page, Statistic, Feedback
from django import forms

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'show_in_menu', 'menu_icon', 'menu_order')
    list_editable = ('show_in_menu', 'menu_icon', 'menu_order')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)
    list_filter = ('is_html',)
    readonly_fields = ('is_html',)  
    actions = ['import_html_pages']
    list_display_links = ('title',)
    ordering = ('menu_order', 'title')

    formfield_overrides = {
        forms.IntegerField: {'widget': forms.NumberInput(attrs={'style': 'width: 70px'})},
    }
    
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
    ordering = ('order',)
    
    class Meta:
        verbose_name = _('статистику')
        verbose_name_plural = _('Статистика')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'is_processed')
    list_editable = ('is_processed',)
    list_filter = ('is_processed', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('name', 'email', 'message', 'created_at')
    date_hierarchy = 'created_at'
    
    class Meta:
        verbose_name = _('обратную связь')
        verbose_name_plural = _('Обратная связь')