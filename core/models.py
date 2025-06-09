import os
from pathlib import Path
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from adminsortable.models import SortableMixin
from adminsortable.fields import SortableForeignKey

class Page(models.Model):
    title = models.CharField(_('Заголовок'), max_length=200)
    slug = models.SlugField(_('URL-адрес'), unique=True, blank=True, 
                        help_text=_('Уникальный идентификатор страницы для URL'))
    content = CKEditor5Field(_('Содержание страницы'), 
                        help_text=_('Основной текст страницы'))
    image = models.ImageField(_('Изображение'), upload_to='pages/', 
                            null=True, blank=True,
                            help_text=_('Изображение для страницы'))
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    show_in_menu = models.BooleanField(_('Отображать в меню'), default=True)
    is_html = models.BooleanField(
        default=False,
        verbose_name='HTML страница',
        help_text='Отметьте, если страница синхронизируется с файлом шаблона'
    )
    
    menu_order = models.PositiveIntegerField(
        _('Порядок в меню'),
        default=0,
        help_text=_('Число для сортировки (меньше - выше в меню)')
    )

    TEMPLATE_MAPPING = {
        'home': 'home.html',
        'general-stats': 'analytics/general_stats.html',
        'demand': 'analytics/demand.html',
        'geography': 'analytics/geography.html',
        'skills': 'analytics/skills.html',
        'latest': 'vacancies/latest.html'
    }
    
    ICON_CHOICES = [
        ('bi-file-earmark-text', 'Документ'),
        ('bi-file-code', 'Код'),
        ('bi-file-text', 'Текст'),
        ('bi-file-richtext', 'Форматированный текст'),
        ('bi-file-break', 'Разрыв'),
        ('bi-file-plus', 'Плюс'),
        ('bi-file-minus', 'Минус'),
        ('bi-file-check', 'Галочка'),
        ('bi-file-x', 'Крестик'),
        ('bi-file-image', 'Изображение'),
        ('bi-file-music', 'Музыка'),
        ('bi-file-play', 'Видео'),
        ('bi-file-zip', 'Архив'),
        ('bi-file-pdf', 'PDF'),
        ('bi-file-word', 'Word'),
        ('bi-file-excel', 'Excel'),
        ('bi-file-ppt', 'PowerPoint'),
        ('bi-house-door', 'Дом'),
        ('bi-bar-chart-line', 'Ступенчатый график'),
        ('bi-graph-up', 'График'),
        ('bi-globe', 'Глобус'),
        ('bi-lightbulb', 'Лампочка'),
        ('bi-briefcase', 'Портфель'),
    ]
    menu_icon = models.CharField(
        _('Иконка меню'),
        max_length=50,
        choices=ICON_CHOICES,
        default='bi-file-earmark-text',
        help_text=_('Выберите иконку для отображения в меню')
    )
    
    class Meta:
        verbose_name = _('страницу')
        verbose_name_plural = _('Страницы')
        ordering = ['menu_order', 'title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        if self.is_html:
            self.update_template_file()

    def update_template_file(self):
        template_path = self.get_template_path()
        if template_path:
            os.makedirs(os.path.dirname(template_path), exist_ok=True)
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(self.content)

    def get_template_path(self):
        template_name = self.TEMPLATE_MAPPING.get(self.slug)
        if not template_name:
            return None
        return Path(settings.BASE_DIR) / 'templates' / template_name

    def load_from_template(self):
        template_path = self.get_template_path()
        if template_path and template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            return True
        return False

    def __str__(self):
        return self.title


class Statistic(models.Model):
    title = models.CharField(_('Название статистики'), max_length=200, 
                        help_text=_('Заголовок для блока статистики'))
    table_html = models.TextField(_('HTML таблицы'), 
                                help_text=_('HTML-код таблицы с данными'))
    chart_image = models.ImageField(_('График'), upload_to='charts/', 
                                help_text=_('Изображение с графиком'))
    page = models.ForeignKey(Page, verbose_name=_('Страница'), 
                        on_delete=models.CASCADE, 
                        related_name='statistics', 
                        help_text=_('Страница, к которой привязана статистика'))
    order = models.PositiveIntegerField(_('Порядок отображения'), default=0, 
                                    help_text=_('Число для сортировки (меньше - выше)'))

    class Meta:
        ordering = ['order']
        verbose_name = _('статистику')
        verbose_name_plural = _('Данные статистики')

    def __str__(self):
        return self.title