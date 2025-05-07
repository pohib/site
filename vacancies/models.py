from django.db import models
from django.utils.translation import gettext_lazy as _

class Vacancy(models.Model):
    title = models.CharField(_('Название вакансии'), max_length=200, help_text=_('Заголовок вакансии'))
    description = models.TextField(_('Описание'), help_text=_('Подробное описание вакансии'))
    skills = models.TextField(_('Требуемые навыки'), help_text=_('Список необходимых навыков'))
    company = models.CharField(_('Компания'), max_length=200, help_text=_('Название компании-работодателя'))
    salary = models.CharField(_('Зарплата'), max_length=100, help_text=_('Уровень зарплаты'))
    region = models.CharField(_('Регион'), max_length=100, help_text=_('Географическое расположение'))
    published_at = models.DateTimeField(_('Дата публикации'), help_text=_('Когда вакансия была опубликована'))
    url = models.URLField(_('Ссылка на вакансию'), help_text=_('URL оригинальной вакансии'))
    company_logo = models.URLField(_('Лого компании'), null=True, blank=True)

    class Meta:
        verbose_name = _('вакансию')
        verbose_name_plural = _('Вакансии')
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['-published_at']),
        ]

    def __str__(self):
        return self.title
    
    @property
    def skills_list(self):
        return [skill.strip() for skill in self.skills.split(',')]
    
    @property
    def short_description(self):
        return self.description[:200] + '...' if len(self.description) > 200 else self.description