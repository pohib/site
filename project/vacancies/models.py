from django.db import models

class Vacancy(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    skills = models.TextField()
    company = models.CharField(max_length=200)
    salary = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    published_at = models.DateTimeField()
    url = models.URLField()

    class Meta:
        ordering = ['-published_at']
        verbose_name_plural = 'Vacancies'

    def __str__(self):
        return self.title