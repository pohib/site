import requests
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Vacancy

def latest_vacancies(request):
    Vacancy.objects.all().delete()
    
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": "C# developer OR C# программист",
        "specialization": 1,  # IT
        "date_from": (timezone.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
        "per_page": 10,
        "order_by": "publication_time"
    }
    
    response = requests.get(url, params=params)
    vacancies_data = response.json().get('items', [])
    
    for vacancy_data in vacancies_data:
        vacancy_detail = requests.get(f"https://api.hh.ru/vacancies/{vacancy_data['id']}").json()
        
        salary = vacancy_data.get('salary')
        salary_str = "Не указана"
        if salary:
            if salary.get('from') and salary.get('to'):
                salary_str = f"{salary['from']} - {salary['to']} {salary['currency']}"
            elif salary.get('from'):
                salary_str = f"от {salary['from']} {salary['currency']}"
            elif salary.get('to'):
                salary_str = f"до {salary['to']} {salary['currency']}"
        
        skills = ", ".join([skill['name'] for skill in vacancy_detail.get('key_skills', [])])
        
        Vacancy.objects.create(
            title=vacancy_data['name'],
            description=vacancy_detail.get('description', ''),
            skills=skills,
            company=vacancy_data['employer']['name'],
            salary=salary_str,
            region=vacancy_data['area']['name'],
            published_at=vacancy_data['published_at'],
            url=vacancy_data['alternate_url']
        )
    
    vacancies = Vacancy.objects.all()
    return render(request, 'vacancies/latest.html', {'vacancies': vacancies})