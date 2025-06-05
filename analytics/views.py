import json
from pathlib import Path
from django.conf import settings
from django.shortcuts import render
from django.core.cache import cache
from .models import SalaryByCity, Skill, AnalyticsSettings, ChartSettings
import logging
from datetime import datetime, timedelta
import requests
import dateutil.parser
from django.utils.timezone import make_aware
from django.utils import timezone


logger = logging.getLogger(__name__)

def load_json_data(filename):
    cache_key = f"analytics_{filename}"
    data = cache.get(cache_key)
    
    if not data:
        try:
            data_path = Path(settings.MEDIA_ROOT) / 'data' / filename
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            cache.set(cache_key, data, timeout=3600)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            data = {}
            
    return data

def normalize_skill_name(name):
    name = name.strip().lower()
    if name.startswith('с#'):
        name = 'c#' + name[2:]
        
    if name == '.net framework':
        return '.NET Framework'
        
    replacements = {
        'asp.net core': 'ASP.NET',
        'ms sql': 'SQL Server',
        'postgresql': 'PostgreSQL'
    }
    
    return replacements.get(name, name)

def general_stats(request):
    salary_data = load_json_data('salary_by_year.json')
    city_salary_data = load_json_data('salary_by_city.json')
    vacancy_share_data = load_json_data('vacancy_share_by_city.json')
    skills_data = load_json_data('top_skills.json')

    salary_by_year = []
    for i in range(len(salary_data.get('years', []))):
        year_data = {
            'year': salary_data['years'][i],
            'average_salary': salary_data['avg_salaries'][i],
            'vacancy_count': salary_data['vacancy_counts'][i],
            'profession_average_salary': salary_data['prof_salaries'][i],
            'profession_vacancy_count': salary_data['prof_vacancy_counts'][i]
        }
        if year_data['vacancy_count'] > 0:
            year_data['profession_share'] = (
                year_data['profession_vacancy_count'] / year_data['vacancy_count']
            ) * 100
        else:
            year_data['profession_share'] = 0
        salary_by_year.append(year_data)

    all_salaries = city_salary_data.get('all_salaries', [])
    overall_avg_salary = sum(all_salaries) / len(all_salaries) if all_salaries else 0

    salary_by_city = []
    for city, salary in zip(city_salary_data.get('cities', []), 
                        city_salary_data.get('csharp_salaries', [])):
        city_data = {
            'city': city,
            'average_salary': salary,
            'difference': ((salary - overall_avg_salary) / overall_avg_salary) * 100 
                        if overall_avg_salary else 0
        }
        salary_by_city.append(city_data)

    vacancy_share_by_city = []
    for city, share in zip(vacancy_share_data.get('cities', []), 
                        vacancy_share_data.get('shares', [])):
        vacancy_share_by_city.append({
            'city': city,
            'vacancy_share': share
        })

    max_skill_count = max(skill['count'] for skill in skills_data.get('top_skills', [])) if skills_data.get('top_skills') else 1
    skills = []
    for skill in skills_data.get('top_skills', []):
        skill_data = {
            'name': skill['display_name'],
            'count': skill['count'],
            'year': skill.get('year', 'N/A'),
            'share': (skill['count'] / max_skill_count) * 100
        }
        skills.append(skill_data)

    return render(request, 'analytics/general_stats.html', {
        'salary_by_year': salary_by_year,
        'salary_by_city': salary_by_city[:10],
        'vacancy_share_by_city': vacancy_share_by_city[:10],
        'skills': skills[:20],
    })

def demand(request):
    data = load_json_data('salary_by_year.json')
    stats = get_vacancies()
    current_year = datetime.now().year
    salary_data = []
    salary_growth = 0
    chart_settings = ChartSettings.objects.filter(chart_type='demand').first()
    
    if len(data.get('avg_salaries', [])) >= 3:
        salaries = data['avg_salaries'][-3:]
        if salaries[0] > 0:
            salary_growth = ((salaries[-1] - salaries[0]) / salaries[0]) * 100
    
    for i in range(len(data.get('years', []))):
        year_data = {
            'year': data['years'][i],
            'salary': data['avg_salaries'][i],
            'vacancy_count': data['vacancy_counts'][i],
            'profession_vacancy_count': data['prof_vacancy_counts'][i]
        }

        if i > 0:
            prev_salary = data['avg_salaries'][i-1]
            if prev_salary > 0:
                year_data['change'] = ((year_data['salary'] - prev_salary) / prev_salary) * 100
            else:
                year_data['change'] = 0
        else:
            year_data['change'] = 0
            
        if year_data['vacancy_count'] > 0:
            year_data['profession_share'] = (
                year_data['profession_vacancy_count'] / year_data['vacancy_count']
            ) * 100
        else:
            year_data['profession_share'] = 0
            
        salary_data.append(year_data)
        
        logger.debug(f"Current year stats: {stats}")
        
        
        
    return render(request, 'analytics/demand.html', {
        'salary_data': salary_data,
        'vacancy_data': [{
            'year': item['year'],
            'count': item['profession_vacancy_count'],
            'share': item['profession_share']
        } for item in salary_data],
        'current_year_stats': stats,
        'current_year' : current_year,
        'salary_growth': salary_growth,
        'chart_settings': chart_settings
    })

def geography(request):
    salary_data = load_json_data('salary_by_city.json')
    share_data = load_json_data('vacancy_share_by_city.json')
    chart_settings = ChartSettings.objects.filter(chart_type='geography').first()
    csharp_salaries = salary_data.get('csharp_salaries', [])
    avg_salary = sum(csharp_salaries) / len(csharp_salaries) if csharp_salaries else 0
    
    salary_by_city = []
    for city, salary in zip(salary_data.get('original_city_names', []), salary_data.get('csharp_salaries', [])):
        salary_by_city.append({
            'city': city,
            'average_salary': salary,
            'difference': ((salary - avg_salary) / avg_salary) * 100 if avg_salary else 0
        })
        
    vacancy_share_by_city = []
    for city, share in zip(share_data.get('cities', []), share_data.get('shares', [])):
        vacancy_share_by_city.append({
            'city': city,
            'vacancy_share': share
        })
    
    all_cities = SalaryByCity.objects.filter(
        is_for_profession=True,
        lat__isnull=False,
        lon__isnull=False
    ).distinct()
    
    map_data = [{
        'name': city.city,
        'lat': city.lat,
        'lon': city.lon,
        'salary': city.average_salary if city.average_salary else 0,
        'share': city.vacancy_share if city.vacancy_share else 0
    } for city in all_cities]
    
    return render(request, 'analytics/geography.html', {
        'salary_by_city': salary_by_city,
        'vacancy_share_by_city': vacancy_share_by_city,
        'map_data': map_data,
        'chart_settings': chart_settings
    })

def skills(request):
    try:
        settings = AnalyticsSettings.objects.first()
        threshold = settings.skill_count_threshold if settings else 50
    except:
        threshold = 50
        
    data = load_json_data('top_skills.json')
    
    skills_agg = {}
    years = set()
    
    chart_settings = ChartSettings.objects.filter(chart_type='skills').first()
    
    if 'skills_by_year' in data:
        for year, year_skills in data['skills_by_year'].items():
            years.add(year)
            for skill in year_skills:
                normalized_name = normalize_skill_name(skill['name'])
                if normalized_name in skills_agg:
                    skills_agg[normalized_name]['count'] += skill['count']
                else:
                    skills_agg[normalized_name] = {
                        'name': skill['name'],
                        'count': skill['count'],
                        'years': {year: skill['count']}
                    }

    all_skills_db = Skill.objects.filter(is_for_profession=True)
    
    for skill in all_skills_db:
        normalized_name = normalize_skill_name(skill.name)
        if normalized_name in skills_agg:
            skills_agg[normalized_name]['count'] += skill.count
            if str(skill.year) in skills_agg[normalized_name]['years']:
                skills_agg[normalized_name]['years'][str(skill.year)] += skill.count
            else:
                skills_agg[normalized_name]['years'][str(skill.year)] = skill.count
        else:
            skills_agg[normalized_name] = {
                'name': skill.name,
                'count': skill.count,
                'years': {str(skill.year): skill.count}
            }
            years.add(str(skill.year))

    sorted_skills_all = sorted(skills_agg.values(), key=lambda x: x['count'], reverse=True)

    sorted_skills_for_table = [skill for skill in sorted_skills_all if skill['count'] >= threshold]
    
    max_count = max(skill['count'] for skill in sorted_skills_all) if sorted_skills_all else 1
    
    skills_for_table = []
    
    for i, skill in enumerate(sorted_skills_for_table, 1):
        percentage = (skill['count'] / max_count) * 100
        skills_for_table.append({
            'position': i,
            'name': skill['name'],
            'count': skill['count'],
            'percentage': round(percentage, 2),
        })

    top_20_skills = sorted_skills_all[:20]
    
    top_5_for_trend = []
    colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b']
    
    for i, skill in enumerate(top_20_skills[:5]):
        years_sorted = sorted(years)
        trend_counts = []
        for year in years_sorted:
            trend_counts.append(skill['years'].get(year, 0))
        
        top_5_for_trend.append({
            'name': skill['name'],
            'years': trend_counts,
            'color': colors[i]
        })
    
    return render(request, 'analytics/skills.html', {
        'skills': skills_for_table,
        'top_20_skills': top_20_skills,
        'top_5_skills': top_5_for_trend,
        'years': sorted(years),
        'chart_settings': chart_settings
    })
    
    
def get_vacancies():
    cache_key = "csharp_vacancies_last_12_months"
    cached_count = cache.get(cache_key)
    
    if cached_count is not None:
        return cached_count
    
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        params = {
            "text": "C# OR .NET",
            "specialization": 1,
            "date_from": start_date.strftime('%Y-%m-%d'),
            "date_to": end_date.strftime('%Y-%m-%d'),
            "per_page": 100,
            "search_field": "name",
        }
        
        response = requests.get("https://api.hh.ru/vacancies", params=params)
        response.raise_for_status()
        
        data = response.json()
        vacancies = data.get('items', [])
        
        salaries = []
        for vacancy in vacancies:
            salary = vacancy.get('salary')
            if salary:
                salary_rub = convert_salary(
                    salary.get('from') or salary.get('to'),
                    salary.get('currency'),
                    dateutil.parser.parse(vacancy.get('published_at')))
                if salary_rub:
                    salaries.append(salary_rub)
        
        if salaries:
            avg_salary = sum(salaries) / len(salaries)
            stats = {
                'avg_salary': round(avg_salary),
                'vacancy_count': data.get('found', 0)
            }
        else:
            stats = {
                'avg_salary': None,
                'vacancy_count': data.get('found', 0)
            }
        
        cache.set(cache_key, stats, 60 * 60 * 24)
        
        return stats
        
    except requests.RequestException as e:
        logger.error(f"Ошибка при запросе к API hh.ru: {str(e)}")
        return {'avg_salary': None, 'vacancy_count': None}
    
    
def convert_salary(salary, currency, published_at):
    if not salary or not currency:
        return None
        
    try:
        if isinstance(published_at, str):
            published_at = dateutil.parser.parse(published_at)
        
        if timezone.is_naive(published_at):
            published_at = make_aware(published_at)
        
        currency = currency.upper().replace('RUR', 'RUB')
        
        if currency == 'RUB':
            return float(salary)
        
        CURRENCY_RATES = {
            'USD': 79.62,
            'EUR': 90.9,
            'KZT': 0.16,
            'UAH': 1.91,
            'BYN': 26.6,
            'GBP': 107.45
        }
        
        rate = CURRENCY_RATES.get(currency)
        if not rate:
            logger.debug(f"Конвертация: неизвестная валюта. currency={currency}")
            return None
            
        return round(float(salary) * rate, 2)
        
    except (ValueError, TypeError) as e:
        logger.error(f"Ошибка конвертации зарплаты: {str(e)}")
        return None