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
    
    return render(request, 'analytics/templates/general_stats.html', {
        'salary_by_year': salary_by_year,
        'salary_by_city': salary_by_city,
        'vacancy_share_by_city': vacancy_share_by_city,
        'skills': skills,
    })

def demand(request):
    salary_by_year = SalaryByYear.objects.all()
    return render(request, 'analytics/templates/demand.html', {
        'salary_by_year': salary_by_year,
    })

def geography(request):
    salary_by_city = SalaryByCity.objects.filter(is_for_profession=True)
    vacancy_share_by_city = SalaryByCity.objects.filter(is_for_profession=True).order_by('-vacancy_share')
    
    return render(request, 'analytics/templates/geography.html', {
        'salary_by_city': salary_by_city,
        'vacancy_share_by_city': vacancy_share_by_city,
    })

def skills(request):
    skills = Skill.objects.filter(is_for_profession=True)
    return render(request, 'analytics/templates/skills.html', {
        'skills': skills,
    })