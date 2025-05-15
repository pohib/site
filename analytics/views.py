import json
from pathlib import Path
from django.conf import settings
from django.shortcuts import render
from django.core.cache import cache
from django.http import JsonResponse
from django.core.paginator import Paginator
import django.db
from .models import SalaryByCity, Skill, AnalyticsSettings
import logging

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
    
    salary_data = []
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

    return render(request, 'analytics/demand.html', {
        'salary_data': salary_data,
        'vacancy_data': [{
            'year': item['year'],
            'count': item['profession_vacancy_count'],
            'share': item['profession_share']
        } for item in salary_data]
    })

def geography(request):
    salary_data = load_json_data('salary_by_city.json')
    share_data = load_json_data('vacancy_share_by_city.json')
    
    csharp_salaries = salary_data.get('csharp_salaries', [])
    avg_salary = sum(csharp_salaries) / len(csharp_salaries) if csharp_salaries else 0
    
    salary_by_city = []
    for city, salary in zip(salary_data.get('cities', []), 
                        salary_data.get('csharp_salaries', [])):
        salary_by_city.append({
            'city': city,
            'average_salary': salary,
            'difference': ((salary - avg_salary) / avg_salary) * 100 if avg_salary else 0
        })
        
    vacancy_share_by_city = []
    for city, share in zip(share_data.get('cities', []), 
                        share_data.get('shares', [])):
        vacancy_share_by_city.append({
            'city': city,
            'vacancy_share': share
        })
    
    all_cities = SalaryByCity.objects.exclude(lat__isnull=True).exclude(lon__isnull=True)
    map_data = [{
        'name': city.city,
        'lat': city.lat,
        'lon': city.lon,
        'salary': city.average_salary if city.average_salary else 0,
        'count': city.vacancy_share if city.vacancy_share else 0
    } for city in all_cities]
    
    return render(request, 'analytics/geography.html', {
        'salary_by_city': salary_by_city[:10],
        'vacancy_share_by_city': vacancy_share_by_city[:10],
        'map_data': map_data,
    })

def skills(request):
    try:
        settings = AnalyticsSettings.objects.first()
        threshold = settings.skill_count_threshold if settings else 50
    except:
        threshold = 50
        
    data = load_json_data('top_skills.json')
    
    skills_by_year = data.get('skills_by_year', {})
    skill_totals = {}
    
    for year, year_skills in skills_by_year.items():
        for skill in year_skills:
            normalized_name = normalize_skill_name(skill['name'])
            if normalized_name in skill_totals:
                skill_totals[normalized_name]['count'] += skill['count']
            else:
                skill_totals[normalized_name] = {
                    'display_name': skill['name'],
                    'count': skill['count']
                }
    
    top_20_skills = sorted(skill_totals.values(), key=lambda x: x['count'], reverse=True)[:20]

    all_skills_db = Skill.objects.filter(is_for_profession=True, count__gte=threshold).order_by('-count')
    
    skills_agg = {}
    for skill in all_skills_db:
        original_name = skill.name.strip()
        normalized_name = normalize_skill_name(original_name)
        
        if normalized_name in skills_agg:
            if skill.count > skills_agg[normalized_name]['count']:
                skills_agg[normalized_name] = {
                    'name': original_name,
                    'count': skill.count,
                    'year': skill.year
                }
        else:
            skills_agg[normalized_name] = {
                'name': original_name,
                'count': skill.count,
                'year': skill.year
            }
    
    all_skills = sorted(skills_agg.values(), key=lambda x: x['count'], reverse=True)
    
    max_count = max(skill['count'] for skill in all_skills) if all_skills else 1
    
    skills_for_table = []
    
    for i, skill in enumerate(all_skills, 1):
        percentage = float(round((skill['count'] / max_count) * 100, 2))
        skills_for_table.append({
            'name': skill['name'],
            'count': skill['count'],
            'year': skill.get('year', 'N/A'),
            'percentage': percentage,
            'change': 0,
            'position': i
        })
        
    top_skills_for_trend = []
    net_framework_found = False
    
    for skill in top_20_skills[:5]:
        top_skills_for_trend.append({
            'display_name': skill['display_name'],
            'count': skill['count']
        })
        if skill['display_name'].lower() == '.net framework':
            net_framework_found = True
    
    if not net_framework_found:
        net_framework_skill = next(
            (skill for skill in top_20_skills if skill['display_name'].lower() == '.net framework'), 
            {'display_name': '.NET Framework', 'count': 0}
        )
        if len(top_skills_for_trend) >= 5:
            top_skills_for_trend[4] = net_framework_skill
        else:
            top_skills_for_trend.append(net_framework_skill)
    
    years = sorted(skills_by_year.keys())
    
    trend_data = []
    colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b']
    
    for i, skill in enumerate(top_skills_for_trend):
        skill_years = []
        normalized_skill_name = normalize_skill_name(skill['display_name']).lower()
        is_net_framework = normalized_skill_name == '.net framework'
        
        for year in years:
            year_skills = skills_by_year.get(year, [])
            
            if is_net_framework:
                skill_count = next(
                    (s['count'] for s in year_skills 
                    if normalize_skill_name(s['name']).lower() in ['.net framework', '.net']), 
                    0
                )
            else:
                skill_count = next(
                    (s['count'] for s in year_skills 
                    if normalize_skill_name(s['name']).lower() == normalized_skill_name), 
                    0
                )
            skill_years.append(skill_count)
            
        trend_data.append({
            'name': skill['display_name'],
            'years': skill_years,
            'color': colors[i]
        })
        
    return render(request, 'analytics/skills.html', {
        'skills': skills_for_table,
        'top_20_skills': top_20_skills,
        'top_5_skills': trend_data,
        'years': years
    })