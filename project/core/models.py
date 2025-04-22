from django.db import models
from django.utils.text import slugify

class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='pages/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Statistic(models.Model):
    title = models.CharField(max_length=200)
    table_html = models.TextField()
    chart_image = models.ImageField(upload_to='charts/')
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='statistics')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title