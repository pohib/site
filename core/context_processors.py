from .models import Page

def dynamic_pages(request):
    return {'dynamic_pages': Page.objects.filter(show_in_menu=True)}
