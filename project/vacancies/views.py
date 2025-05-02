import requests
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Vacancy
from datetime import datetime
from django.core.cache import cache
from django.utils.timezone import make_aware
from xml.etree import ElementTree as ET
from django.conf import settings

MAX_SALARY = 10_000_000

def latest_vacancies(request):
    Vacancy.objects.all().delete()
    
    try:
        url = "https://api.hh.ru/vacancies"
        params = {
            "text": "C# developer OR C# программист",
            "specialization": 1,  # IT
            "date_from": (timezone.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            "per_page": 10,
            "order_by": "publication_time"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        vacancies_data = response.json().get('items', [])
        
        for vacancy_data in vacancies_data:
            try:
                vacancy_detail = requests.get(
                    f"https://api.hh.ru/vacancies/{vacancy_data['id']}",
                    timeout=10
                ).json()
                
                salary = vacancy_data.get('salary')
                salary_str = "Не указана"
                
                if salary:
                    salary_from = salary.get('from')
                    salary_to = salary.get('to')
                    currency = salary.get('currency')
                    
                    if currency and (salary_from or salary_to):
                        if salary_from and salary_to:
                            from_rub = convert_salary(salary_from, currency, vacancy_data['published_at'])
                            to_rub = convert_salary(salary_to, currency, vacancy_data['published_at'])
                            
                            if from_rub and to_rub:
                                if from_rub > MAX_SALARY or to_rub > MAX_SALARY:
                                    salary_str = "Зарплата не указана (некорректные данные)"
                                else:
                                    salary_str = f"{int(from_rub):,} - {int(to_rub):,} руб".replace(',', ' ')
                        elif salary_from:
                            salary_rub = convert_salary(salary_from, currency, vacancy_data['published_at'])
                            if salary_rub:
                                if salary_rub > MAX_SALARY:
                                    salary_str = "Зарплата не указана (некорректные данные)"
                                else:
                                    salary_str = f"от {int(salary_rub):,} руб".replace(',', ' ')
                        elif salary_to:
                            salary_rub = convert_salary(salary_to, currency, vacancy_data['published_at'])
                            if salary_rub:
                                if salary_rub > MAX_SALARY:
                                    salary_str = "Зарплата не указана (некорректные данные)"
                                else:
                                    salary_str = f"до {int(salary_rub):,} руб".replace(',', ' ')
                
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
                
            except (requests.RequestException, KeyError, ValueError) as e:
                print(f"Ошибка при обработке вакансии {vacancy_data.get('id')}: {str(e)}")
                continue
        
        vacancies = Vacancy.objects.all().order_by('-published_at')
        return render(request, 'vacancies/latest.html', {'vacancies': vacancies})
        
    except requests.RequestException as e:
        print(f"Ошибка при запросе к API HH: {str(e)}")
        return render(request, 'vacancies/latest.html', {'vacancies': [], 'error': str(e)})

def get_cbr_currency_rate(currency_code, date):
    """Получает курс валюты от ЦБ РФ на указанную дату"""
    if settings.DEBUG:
        MOCK_RATES = {
            'USD': 75.45, 
            'EUR': 85.32,
            'KZT': 0.18,
            'UAH': 2.05,
            'BYN': 28.50,
            'GBP': 95.60
        }
        return MOCK_RATES.get(currency_code.upper())
    
    cache_key = f'cbr_rate_{currency_code}_{date.strftime("%Y-%m-%d")}'
    cached_rate = cache.get(cache_key)
    
    if cached_rate is not None:
        return cached_rate

    formatted_date = date.strftime('%d/%m/%Y')
    url = f'https://www.cbr.ru/scripts/XML_daily.asp?date_req={formatted_date}'
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        currency_map = {
            'USD': 'R01235',
            'EUR': 'R01239',
            'KZT': 'R01335',
            'UAH': 'R01720',
            'BYN': 'R01090B',
            'GBP': 'R01035',
        }
        
        cbr_code = currency_map.get(currency_code.upper())
        if not cbr_code:
            return None
            
        for valute in root.findall('Valute'):
            if valute.find('CharCode').text == currency_code.upper():
                nominal = int(valute.find('Nominal').text)
                value = float(valute.find('Value').text.replace(',', '.'))
                rate = value / nominal
                cache.set(cache_key, rate, timeout=60*60*24*7)
                return rate
                
    except (requests.RequestException, ET.ParseError) as e:
        print(f"Ошибка при получении курса валют: {str(e)}")
        return None

def convert_salary(salary, currency, published_at):
    if not salary or not currency:
        return None
        
    try:
        if isinstance(published_at, str):
            published_at = make_aware(datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%S%z'))
        
        if currency.upper() in ('RUB', 'RUR'):
            return float(salary)
            
        rate = get_cbr_currency_rate(currency, published_at)
        if not rate:
            return None
            
        return round(float(salary) * rate, 2)
        
    except (ValueError, TypeError) as e:
        print(f"Ошибка конвертации зарплаты: {str(e)}")
        return None