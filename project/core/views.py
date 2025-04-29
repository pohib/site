from django.shortcuts import render, get_object_or_404
from .models import Page

def home(request):
    page = get_object_or_404(Page, slug='home')
    return render(request, 'home.html', {'page': page})

def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug)
    return render(request, 'page.html', {'page': page})