from django.shortcuts import render
from .models import (
    SalaryByYear, 
    SalaryByCity, 
    Skill
)

def general_stats(request):
    salary_by_year = SalaryByYear.objects.all()
    salary_by_city = SalaryByCity.objects.filter(is_for_profession=False)
    vacancy_share_by_city = SalaryByCity.objects.filter(is_for_profession=False).order_by('-vacancy_share')
    skills = Skill.objects.filter(is_for_profession=False)
    
    return render(request, 'analytics/general_stats.html', {
        'salary_by_year': salary_by_year,
        'salary_by_city': salary_by_city,
        'vacancy_share_by_city': vacancy_share_by_city,
        'skills': skills,
    })

def demand(request):
    salary_by_year = SalaryByYear.objects.all()
    return render(request, 'analytics/demand.html', {
        'salary_by_year': salary_by_year,
    })

def geography(request):
    salary_by_city = SalaryByCity.objects.filter(is_for_profession=True).order_by('-average_salary')[:10]
    vacancy_share_by_city = SalaryByCity.objects.filter(is_for_profession=True).order_by('-vacancy_share')[:10]

    all_cities = SalaryByCity.objects.exclude(lat__isnull=True).exclude(lon__isnull=True)

    map_data = []
    for city in all_cities:
        map_data.append({
            'name': city.city,
            'lat': city.lat,
            'lon': city.lon,
            'salary': city.average_salary if city.average_salary else 0,
            'count': city.vacancy_share if city.vacancy_share else 0
        })
    
    return render(request, 'analytics/geography.html', {
        'salary_by_city': salary_by_city,
        'vacancy_share_by_city': vacancy_share_by_city,
        'map_data': map_data,
    })

def skills(request):
    skills = Skill.objects.filter(is_for_profession=True)
    return render(request, 'analytics/skills.html', {
        'skills': skills,
    })