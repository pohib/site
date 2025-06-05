from django.shortcuts import render, get_object_or_404
from .models import Page
from django.http import HttpResponse

def home(request):
    page, created = Page.objects.get_or_create(
        slug='home',
        defaults={
            'title': 'Главная',
            'content': 'SAMPLE TEXT'
        }
    )
    return render(request, 'home.html', {'page': page})

def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug)
    
    if page.is_html:
        try:
            with open(page.get_template_path(), 'r', encoding='utf-8') as f:
                page.content = f.read()
        except FileNotFoundError:
            pass
    
    return render(request, 'page.html', {'page': page})