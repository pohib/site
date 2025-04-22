from django.db import models

class SalaryByYear(models.Model):
    year = models.IntegerField()
    average_salary = models.FloatField()
    vacancy_count = models.IntegerField()
    profession_average_salary = models.FloatField(null=True, blank=True)
    profession_vacancy_count = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['year']

    def __str__(self):
        return f"Статистика за {self.year} год"

class SalaryByCity(models.Model):
    city = models.CharField(max_length=100)
    average_salary = models.FloatField()
    vacancy_share = models.FloatField()
    is_for_profession = models.BooleanField(default=False)

    class Meta:
        ordering = ['-average_salary']

    def __str__(self):
        return f"Зарплаты в {self.city}"

class Skill(models.Model):
    name = models.CharField(max_length=100)
    year = models.IntegerField()
    count = models.IntegerField()
    is_for_profession = models.BooleanField(default=False)

    class Meta:
        ordering = ['-year', '-count']

    def __str__(self):
        return f"{self.name} ({self.year})"