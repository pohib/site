from django.db import models
from django.utils.translation import gettext_lazy as _

class SalaryByYear(models.Model):
    year = models.IntegerField(_('Год'), help_text=_('Год сбора статистики'))
    average_salary = models.FloatField(_('Средняя зарплата'), help_text=_('Средняя зарплата в рублях'))
    vacancy_count = models.IntegerField(_('Количество вакансий'), help_text=_('Общее число вакансий'))
    profession_average_salary = models.FloatField(
        _('Зарплата C# разработчика'), 
        null=True, 
        blank=True,
        help_text=_('Средняя зарплата для C# разработчиков')
    )
    profession_vacancy_count = models.IntegerField(
        _('Вакансии C# разработчика'),
        null=True,
        blank=True,
        help_text=_('Количество вакансий для C# разработчиков')
    )

    class Meta:
        verbose_name = _('статистику по годам')
        verbose_name_plural = _('Статистика по годам')
        ordering = ['year']

    def __str__(self):
        return _("Статистика за {} год").format(self.year)

class SalaryByCity(models.Model):
    city = models.CharField(_('Город'), max_length=100, help_text=_('Название города'))
    average_salary = models.FloatField(_('Средняя зарплата'), help_text=_('Средняя зарплата в рублях'))
    vacancy_share = models.FloatField(_('Доля вакансий'), help_text=_('Доля вакансий в процентах'))
    is_for_profession = models.BooleanField(
        _('Только для C# разработчиков'),
        default=False,
        help_text=_('Отметка для статистики по конкретной профессии')
    )
    lat = models.FloatField(_('Широта'), help_text = _('Координата X от экватора'), null=True, blank=True)
    lon = models.FloatField(_('Долгота'), help_text = _('Координата Y от экватора'), null=True, blank=True)

    class Meta:
        verbose_name = _('статистику по городам')
        verbose_name_plural = _('Статистика по городам')
        ordering = ['-average_salary']
        db_table = 'salary_by_city'

    def __str__(self):
        return _("Зарплаты в {}").format(self.city)

class Skill(models.Model):
    name = models.CharField(_('Навык'), max_length=100, help_text=_('Название навыка'))
    year = models.IntegerField(_('Год'), help_text=_('Год сбора данных'))
    count = models.IntegerField(_('Количество упоминаний'), help_text=_('Частота упоминания навыка'))
    is_for_profession = models.BooleanField(
        _('Только для C# разработчиков'),
        default=False,
        help_text=_('Отметка для навыков конкретной профессии')
    )

    class Meta:
        verbose_name = _('Навык')
        verbose_name_plural = _('Навыки')
        ordering = ['-year', '-count']
        indexes = [
            models.Index(fields=['-count', 'name']),
            models.Index(fields=['is_for_profession', '-count']),
        ]

    def __str__(self):
        return _("{} ({})").format(self.name, self.year)
    
class AnalyticsSettings(models.Model):
    skill_count_threshold = models.IntegerField(
        _('Порог частоты навыков'),
        default=50,
        help_text=_('Навыки с частотой ниже этого значения не будут отображаться')
    )
    
    class Meta:
        verbose_name = _('настройку аналитики')
        verbose_name_plural = _('Настройки аналитики')

    def __str__(self):
        return f"Настройки аналитики (порог: {self.skill_count_threshold})"