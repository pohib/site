from .models import Page

def dynamic_pages(request):
    pages = Page.objects.filter(show_in_menu=True).exclude(slug='').order_by('menu_order', 'title')
    return {'dynamic_pages': pages}