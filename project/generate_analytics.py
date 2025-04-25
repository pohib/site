import os
import django
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from django.conf import settings
from matplotlib.ticker import FuncFormatter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'csharp_dev.settings')
django.setup()

from analytics.models import SalaryByYear, SalaryByCity, Skill

def format_thousands(x, pos):
    return f'{int(x):,}'.replace(',', ' ')

thousands_formatter = FuncFormatter(format_thousands)

def generate_salary_by_year_chart():
    data = SalaryByYear.objects.all().order_by('year')
    years = [item.year for item in data]
    avg_salaries = [item.average_salary for item in data]
    prof_salaries = [item.profession_average_salary for item in data if item.profession_average_salary]
    
    plt.figure(figsize=(12, 6))
    bar_width = 0.35
    index = np.arange(len(years))

    bars1 = plt.bar(index, avg_salaries, bar_width, label='Все вакансии', color='#2394d2')
    if prof_salaries:
        bars2 = plt.bar(index + bar_width, prof_salaries, bar_width, label='C# разработчик', color='#28a745')
    
    plt.title('Динамика уровня зарплат по годам', pad=20, fontsize=14, fontweight='bold')
    plt.xlabel('Год', labelpad=10)
    plt.ylabel('Средняя зарплата, руб', labelpad=10)
    plt.xticks(index + bar_width / 2, years)
    plt.gca().yaxis.set_major_formatter(thousands_formatter)
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    for bar in bars1:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{height:,.0f}'.replace(',', ' '),
                 ha='center', va='bottom', fontsize=9)
    
    if prof_salaries:
        for bar in bars2:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:,.0f}'.replace(',', ' '),
                     ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(os.path.join(settings.MEDIA_ROOT, 'charts', 'salary_by_year.png'), dpi=150, bbox_inches='tight')
    plt.close()

def generate_vacancies_by_year_chart():
    data = SalaryByYear.objects.all().order_by('year')
    years = [item.year for item in data]
    total_vacancies = [item.vacancy_count for item in data]
    prof_vacancies = [item.profession_vacancy_count for item in data if item.profession_vacancy_count]
    
    plt.figure(figsize=(12, 6))
    
    line1, = plt.plot(years, total_vacancies, 'o-', label='Все вакансии', color='#2394d2', linewidth=2, markersize=8)
    if prof_vacancies:
        line2, = plt.plot(years[:len(prof_vacancies)], prof_vacancies, 's-', label='C# разработчик', 
                         color='#28a745', linewidth=2, markersize=8)
    
    plt.title('Динамика количества вакансий по годам', pad=20, fontsize=14, fontweight='bold')
    plt.xlabel('Год', labelpad=10)
    plt.ylabel('Количество вакансий', labelpad=10)
    plt.gca().yaxis.set_major_formatter(thousands_formatter)
    plt.legend()
    plt.grid(linestyle='--', alpha=0.7)

    for x, y in zip(years, total_vacancies):
        plt.text(x, y, f'{y:,}'.replace(',', ' '), 
                 ha='center', va='bottom', fontsize=9)
    
    if prof_vacancies:
        for x, y in zip(years[:len(prof_vacancies)], prof_vacancies):
            plt.text(x, y, f'{y:,}'.replace(',', ' '), 
                     ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(os.path.join(settings.MEDIA_ROOT, 'charts', 'vacancies_by_year.png'), dpi=150, bbox_inches='tight')
    plt.close()

def generate_salary_by_city_chart():
    data = SalaryByCity.objects.filter(is_for_profession=False).order_by('-average_salary')[:10]
    cities = [item.city for item in data]
    salaries = [item.average_salary for item in data]
    
    plt.figure(figsize=(12, 6))
    bars = plt.barh(cities[::-1], salaries[::-1], color='#2394d2')
    
    plt.title('Уровень зарплат по городам (ТОП-10)', pad=20, fontsize=14, fontweight='bold')
    plt.xlabel('Средняя зарплата, руб', labelpad=10)
    plt.gca().xaxis.set_major_formatter(thousands_formatter)
    plt.grid(axis='x', linestyle='--', alpha=0.7)

    for bar in bars:
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2., 
                 f'{width:,.0f}'.replace(',', ' '),
                 ha='left', va='center', fontsize=9, pad=5)
    
    plt.tight_layout()
    plt.savefig(os.path.join(settings.MEDIA_ROOT, 'charts', 'salary_by_city.png'), dpi=150, bbox_inches='tight')
    plt.close()

def generate_vacancy_share_by_city_chart():
    data = SalaryByCity.objects.filter(is_for_profession=False).order_by('-vacancy_share')[:10]
    cities = [item.city for item in data]
    shares = [item.vacancy_share for item in data]

    explode = [0.1] + [0]*(len(cities)-1)
    
    plt.figure(figsize=(10, 10))
    colors = plt.cm.Paired(np.linspace(0, 1, len(cities)))
    patches, texts, autotexts = plt.pie(shares, explode=explode, labels=cities, colors=colors,
                                        autopct='%1.1f%%', startangle=140, pctdistance=0.85,
                                        textprops={'fontsize': 9})
    
    plt.title('Доля вакансий по городам (ТОП-10)', pad=20, fontsize=14, fontweight='bold')

    for autotext in autotexts:
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')
    
    # Добавляем белую обводку
    for patch in patches:
        patch.set_edgecolor('white')
        patch.set_linewidth(0.5)
    
    plt.tight_layout()
    plt.savefig(os.path.join(settings.MEDIA_ROOT, 'charts', 'vacancy_share_by_city.png'), 
                dpi=150, bbox_inches='tight')
    plt.close()

def generate_top_skills_chart():
    skills = Skill.objects.filter(is_for_profession=False).order_by('-count')[:20]
    skill_names = [skill.name for skill in skills]
    counts = [skill.count for skill in skills]
    
    plt.figure(figsize=(12, 8))
    bars = plt.barh(skill_names[::-1], counts[::-1], color='#2394d2')
    
    plt.title('ТОП-20 наиболее востребованных навыков', pad=20, fontsize=14, fontweight='bold')
    plt.xlabel('Количество упоминаний', labelpad=10)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Добавление значений на столбцы
    for bar in bars:
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2., 
                 f'{width:,}'.replace(',', ' '),
                 ha='left', va='center', fontsize=9, pad=5)
    
    plt.tight_layout()
    plt.savefig(os.path.join(settings.MEDIA_ROOT, 'charts', 'top_skills.png'), dpi=150, bbox_inches='tight')
    plt.close()

def generate_all_charts():
    os.makedirs(os.path.join(settings.MEDIA_ROOT, 'charts'), exist_ok=True)
    
    print("Генерация графиков...")
    generate_salary_by_year_chart()
    generate_vacancies_by_year_chart()
    generate_salary_by_city_chart()
    generate_vacancy_share_by_city_chart()
    generate_top_skills_chart()
    print("Все графики успешно сгенерированы!")

if __name__ == '__main__':
    generate_all_charts()