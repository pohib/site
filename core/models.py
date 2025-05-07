from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

class Page(models.Model):
    title = models.CharField(_('Заголовок'), max_length=200)
    slug = models.SlugField(_('URL-адрес'), unique=True, blank=True, help_text=_('Уникальный идентификатор страницы для URL'))
    content = CKEditor5Field(_('Содержание страницы'), help_text=_('Основной текст страницы'))
    image = models.ImageField(_('Изображение'), upload_to='pages/', 
                            null=True, blank=True,
                            help_text=_('Изображение для страницы'))
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    is_html = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('страницу')
        verbose_name_plural = _('Страницы')
        ordering = ['title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Statistic(models.Model):
    title = models.CharField(_('Название статистики'), max_length=200, help_text=_('Заголовок для блока статистики'))
    table_html = models.TextField(_('HTML таблицы'), help_text=_('HTML-код таблицы с данными'))
    chart_image = models.ImageField(_('График'), upload_to='charts/', help_text=_('Изображение с графиком'))
    page = models.ForeignKey(Page, verbose_name=_('Страница'), on_delete=models.CASCADE, related_name='statistics', help_text=_('Страница, к которой привязана статистика'))
    order = models.PositiveIntegerField(_('Порядок отображения'), default=0, help_text=_('Число для сортировки (меньше - выше)'))

    class Meta:
        verbose_name = _('статистику')
        verbose_name_plural = _('Данные статистики')
        ordering = ['order']

    def __str__(self):
        return self.title