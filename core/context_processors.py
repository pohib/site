from .models import Page
from django.conf import settings

def dynamic_pages(request):
    pages = Page.objects.filter(show_in_menu=True).exclude(slug='').order_by('menu_order', 'title')
    return {'dynamic_pages': pages, 'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY}