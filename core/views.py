from django.shortcuts import render, get_object_or_404
from .models import Page, Feedback
from django.core.mail import send_mail
from django.conf import settings
import requests
from django.http import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

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

def contact_view(request):
    if request.method == 'POST':
        errors = {}
        data = request.POST

        name = data.get('name', '').strip()
        if not name:
            errors['name'] = ['Введите ваше имя']

        email = data.get('email', '').strip()
        if not email:
            errors['email'] = ['Введите email']
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors['email'] = ['Введите корректный email']

        message = data.get('message', '').strip()
        if not message:
            errors['message'] = ['Введите сообщение']

        recaptcha_response = data.get('g-recaptcha-response')
        if not recaptcha_response:
            errors['captcha'] = ['Подтвердите, что вы не робот']
        else:
            verify_data = {
                'secret': settings.RECAPTCHA_PRIVATE_KEY,
                'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=verify_data)
            result = r.json()
            if not result.get('success'):
                errors['captcha'] = ['Ошибка проверки reCAPTCHA']
        
        if errors:
            return JsonResponse({'success': False, 'errors': errors})
        
        try:
            feedback = Feedback.objects.create(
                name=name,
                email=email,
                message=message
            )
            
            send_mail(
                f'Новое сообщение от {name}',
                f'Имя: {name}\nEmail: {email}\n\nСообщение:\n{message}',
                settings.DEFAULT_FROM_EMAIL,
                ['vedenyov10@gmail.com'],
                fail_silently=False,
            )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})
