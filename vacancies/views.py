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
import logging
import re

logger = logging.getLogger(__name__)
MAX_SALARY = 10_000_000

def is_primary_csharp_vacancy(vacancy_name, description):
    name_pattern = re.compile(r'C#|\.NET|c\s*sharp', re.IGNORECASE)
    desc_pattern = re.compile(r'(требован(ия|ий)|требуется|ищем|ищется).*?(C#|\.NET|c\s*sharp)', re.IGNORECASE)
    
    if not name_pattern.search(vacancy_name):
        return False
    
    if description and desc_pattern.search(description):
        return True
    
    return True

def latest_vacancies(request):
    try:
        sort_by = request.GET.get('sort', None)
        order = request.GET.get('order', 'desc')
        city_filter = request.GET.get('city', None)

        params = {
            "text": "C# developer OR C# программист",
            "specialization": 1,
            "date_from": (timezone.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            "per_page": 100,
            "order_by": "publication_time",
            "area": 113
        }
        
        logger.info(f"Requesting vacancies with params: {params}")
        response = requests.get("https://api.hh.ru/vacancies", params=params, timeout=10)
        response.raise_for_status()       
        
        vacancies_data = response.json().get('items', [])
        if not vacancies_data:
            logger.warning("API returned empty vacancies list")
            return render(request, 'vacancies/latest.html', {
                'vacancies': [],
                'error': "На данный момент нет свежих вакансий."
            })
        
        vacancies = []
        for vacancy_data in vacancies_data:
            try:
                if not vacancy_data.get('id'):
                    logger.warning("Vacancy without ID skipped")
                    continue
                    
                if not vacancy_data.get('salary'):
                    continue
                    
                detail_response = requests.get(
                    f"https://api.hh.ru/vacancies/{vacancy_data['id']}",
                    timeout=10
                )
                detail_response.raise_for_status()
                vacancy_detail = detail_response.json()
                
                if not is_primary_csharp_vacancy(vacancy_data.get('name', ''), vacancy_detail.get('description', '')):
                    continue
                
                salary = vacancy_data.get('salary', {})
                salary_from = salary.get('from')
                salary_to = salary.get('to')
                currency = salary.get('currency', '').upper().replace('RUR', 'RUB')

                salary_value = salary_from if salary_from else salary_to if salary_to else 0
                if salary_value:
                    salary_value = convert_salary(salary_value, currency, vacancy_data.get('published_at')) or 0

                salary_str = ""
                if salary_from and salary_to:
                    salary_str = f"{salary_from:,} - {salary_to:,} {currency}".replace(',', ' ')
                elif salary_from:
                    salary_str = f"от {salary_from:,} {currency}".replace(',', ' ')
                elif salary_to:
                    salary_str = f"до {salary_to:,} {currency}".replace(',', ' ')

                skills = ", ".join([skill.get('name', '') for skill in vacancy_detail.get('key_skills', [])])
                
                employer = vacancy_data.get('employer', {})
                logo_url = employer.get('logo_urls', {}).get('90') if employer else None
                
                area = vacancy_data.get('area', {})
                region = area.get('name', '') if area else ''
                
                if city_filter and city_filter.lower() not in region.lower():
                    continue
                
                vacancy = Vacancy.objects.create(
                    title=vacancy_data.get('name', 'Без названия'),
                    description=vacancy_detail.get('description', ''),
                    skills=skills,
                    company=employer.get('name', ''),
                    salary=salary_str,
                    salary_value=salary_value,
                    region=region,
                    published_at=vacancy_data.get('published_at'),
                    url=vacancy_data.get('alternate_url', '#'),
                    company_logo=logo_url
                )
                vacancies.append(vacancy)
                
                if len(vacancies) >= 10:
                    break
                
            except (requests.RequestException, KeyError, AttributeError) as e:
                logger.error(f"Error processing vacancy {vacancy_data.get('id')}: {str(e)}", exc_info=True)
                continue
        
        Vacancy.objects.exclude(id__in=[v.id for v in vacancies]).delete()
        
        if sort_by == 'salary':
            reverse_order = order == 'desc'
            vacancies.sort(key=lambda x: x.salary_value or 0, reverse=reverse_order)
        elif sort_by == 'city':
            reverse_order = order == 'desc'
            vacancies.sort(key=lambda x: x.region or '', reverse=reverse_order)
        
        all_cities = list(set(v.region for v in Vacancy.objects.all() if v.region))
        
        return render(request, 'vacancies/latest.html', {
            'vacancies': vacancies,
            'sort_by': sort_by,
            'order': order,
            'selected_city': city_filter,
            'all_cities': sorted(all_cities),
            'current_url': request.path
        })
        
    except requests.RequestException as e:
        logger.error(f"API request error: {str(e)}", exc_info=True)
        vacancies = Vacancy.objects.order_by('-published_at')[:10]
        all_cities = list(set(v.region for v in Vacancy.objects.all() if v.region))
        return render(request, 'vacancies/latest.html', {
            'vacancies': vacancies,
            'all_cities': sorted(all_cities),
            'error': "Не удалось загрузить свежие вакансии. Показаны последние сохраненные данные."
        })
        
def get_cbr_currency_rate(currency_code, date):
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
        if isinstance(published_at, datetime):
            if timezone.is_aware(published_at):
                pass
            else:
                published_at = make_aware(published_at)

        elif isinstance(published_at, str):
            try:
                published_at = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%S%z')
                if timezone.is_naive(published_at):
                    published_at = make_aware(published_at)
            except ValueError:
                published_at = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%S')
                published_at = make_aware(published_at)
        
        currency = currency.upper().replace('RUR', 'RUB')
        
        if currency == 'RUB':
            return float(salary)
            
        rate = get_cbr_currency_rate(currency, published_at)
        if not rate:
            return None
            
        return round(float(salary) * rate, 2)
        
    except (ValueError, TypeError) as e:
        logger.error(f"Ошибка конвертации зарплаты: {str(e)}", exc_info=True)
        return None