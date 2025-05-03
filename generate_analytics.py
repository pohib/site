import os
import django
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from django.conf import settings
from matplotlib.ticker import FuncFormatter
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Site.settings')
django.setup()

from analytics.models import SalaryByYear, SalaryByCity, Skill

MAX_SALARY = 10000000
CHART_STYLES = {
    'colors': {
        'general': '#2394d2',
        'profession': '#28a745',
        'secondary': '#6c757d',
        'highlight': '#dc3545'
    },
    'figure_size': (12, 6),
    'dpi': 150
}

def setup_environment():
    charts_dir = Path(settings.MEDIA_ROOT) / 'charts'
    charts_dir.mkdir(parents=True, exist_ok=True)
    return charts_dir

def format_currency(x, pos):
    return f'{int(x):,}'.replace(',', ' ')

currency_formatter = FuncFormatter(format_currency)

def filter_extreme_salaries(data, field_name):
    return [x if x <= MAX_SALARY else None for x in data]

def generate_salary_by_year_chart():
    try:
        data = SalaryByYear.objects.all().order_by('year')
        if not data:
            logger.warning("Нет данных для salary_by_year_chart")
            return
        years = []
        avg_salaries = []
        prof_salaries = []
        
        for item in data:
            if item.profession_average_salary is not None:
                years.append(item.year)
                avg_salaries.append(item.average_salary if item.average_salary <= MAX_SALARY else None)
                prof_salaries.append(item.profession_average_salary if item.profession_average_salary <= MAX_SALARY else None)

        if not years:
            logger.warning("Нет данных по профессии для salary_by_year_chart")
            return

        plt.figure(figsize=CHART_STYLES['figure_size'])
        bar_width = 0.25
        index = np.arange(len(years))

        bars1 = plt.bar(
            index, 
            avg_salaries, 
            bar_width, 
            label='Все вакансии', 
            color=CHART_STYLES['colors']['general']
        )
        bars2 = plt.bar(
            index + bar_width/2,  # Сдвиг вправо
            prof_salaries,
            bar_width,
            label='C# разработчик',
            color=CHART_STYLES['colors']['profession']
        )
        
        if any(prof_salaries):
            bars2 = plt.bar(
                index + bar_width, 
                prof_salaries, 
                bar_width, 
                label='C# разработчик', 
                color=CHART_STYLES['colors']['profession']
            )

        plt.title('Динамика уровня зарплат по годам', pad=20, fontsize=14, fontweight='bold')
        plt.xlabel('Год', labelpad=10)
        plt.ylabel('Средняя зарплата, руб', labelpad=10)
        plt.xticks(index + bar_width / 2, years)
        plt.gca().yaxis.set_major_formatter(currency_formatter)
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)



        if any(prof_salaries):
            for bar in bars2:
                height = bar.get_height()
                if height:
                    plt.text(
                        bar.get_x() + bar.get_width()/2., 
                        height,
                        f'{height:,.0f}'.replace(',', ' '),
                        ha='center', 
                        va='bottom', 
                        fontsize=9
                    )

        plt.tight_layout()
        output_path = Path(settings.MEDIA_ROOT) / 'charts' / 'salary_by_year.png'
        plt.savefig(output_path, dpi=CHART_STYLES['dpi'], bbox_inches='tight')
        plt.close()
        logger.info(f"График сохранен: {output_path}")

    except Exception as e:
        logger.error(f"Ошибка генерации salary_by_year_chart: {str(e)}")
        raise

def generate_vacancies_by_year_chart():
    try:
        data = SalaryByYear.objects.all().order_by('year')
        if not data:
            logger.warning("Нет данных для vacancies_by_year_chart")
            return

        years = [item.year for item in data]
        total_vacancies = [item.vacancy_count for item in data]
        prof_vacancies = [item.profession_vacancy_count for item in data if item.profession_vacancy_count]

        plt.figure(figsize=CHART_STYLES['figure_size'])
        
        line1 = plt.plot(
            years, 
            total_vacancies, 
            'o-', 
            label='Все вакансии', 
            color=CHART_STYLES['colors']['general'], 
            linewidth=2, 
            markersize=8
        )
        
        if any(prof_vacancies):
            line2 = plt.plot(
                years[:len(prof_vacancies)], 
                prof_vacancies, 
                's-', 
                label='C# разработчик', 
                color=CHART_STYLES['colors']['profession'], 
                linewidth=2, 
                markersize=8
            )

        plt.title('Динамика количества вакансий по годам', pad=20, fontsize=14, fontweight='bold')
        plt.xlabel('Год', labelpad=10)
        plt.ylabel('Количество вакансий', labelpad=10)
        plt.gca().yaxis.set_major_formatter(currency_formatter)
        plt.legend()
        plt.grid(linestyle='--', alpha=0.7)

        for x, y in zip(years, total_vacancies):
            plt.text(
                x, y, 
                f'{y:,}'.replace(',', ' '), 
                ha='center', 
                va='bottom', 
                fontsize=9
            )

        if any(prof_vacancies):
            for x, y in zip(years[:len(prof_vacancies)], prof_vacancies):
                plt.text(
                    x, y, 
                    f'{y:,}'.replace(',', ' '), 
                    ha='center', 
                    va='bottom', 
                    fontsize=9
                )

        plt.tight_layout()
        output_path = Path(settings.MEDIA_ROOT) / 'charts' / 'vacancies_by_year.png'
        plt.savefig(output_path, dpi=CHART_STYLES['dpi'], bbox_inches='tight')
        plt.close()
        logger.info(f"График сохранен: {output_path}")

    except Exception as e:
        logger.error(f"Ошибка генерации vacancies_by_year_chart: {str(e)}")
        raise

def generate_salary_by_city_chart():
    try:
        data = SalaryByCity.objects.filter(is_for_profession=False).order_by('-average_salary')[:10]
        if not data:
            logger.warning("Нет данных для salary_by_city_chart")
            return

        cities = [item.city for item in data]
        salaries = filter_extreme_salaries([item.average_salary for item in data], 'average_salary')

        plt.figure(figsize=CHART_STYLES['figure_size'])
        bars = plt.barh(
            cities[::-1], 
            salaries[::-1], 
            color=CHART_STYLES['colors']['general']
        )

        plt.title('Уровень зарплат по городам (ТОП-10)', pad=20, fontsize=14, fontweight='bold')
        plt.xlabel('Средняя зарплата, руб', labelpad=10)
        plt.gca().xaxis.set_major_formatter(currency_formatter)
        plt.grid(axis='x', linestyle='--', alpha=0.7)

        for bar in bars:
            width = bar.get_width()
            if width:
                plt.text(
                    width, 
                    bar.get_y() + bar.get_height()/2., 
                    f'{width:,.0f}'.replace(',', ' '),
                    ha='left', 
                    va='center', 
                    fontsize=9, 
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=2)
                )

        plt.tight_layout()
        output_path = Path(settings.MEDIA_ROOT) / 'charts' / 'salary_by_city.png'
        plt.savefig(output_path, dpi=CHART_STYLES['dpi'], bbox_inches='tight')
        plt.close()
        logger.info(f"График сохранен: {output_path}")

    except Exception as e:
        logger.error(f"Ошибка генерации salary_by_city_chart: {str(e)}")
        raise

def generate_vacancy_share_by_city_chart():
    try:
        data = SalaryByCity.objects.filter(is_for_profession=False).order_by('-vacancy_share')[:10]
        if not data:
            logger.warning("Нет данных для vacancy_share_by_city_chart")
            return

        cities = [item.city for item in data]
        shares = [item.vacancy_share for item in data]
        explode = [0.1] + [0]*(len(cities)-1)

        plt.figure(figsize=(10, 10))
        colors = plt.cm.Paired(np.linspace(0, 1, len(cities)))
        patches, texts, autotexts = plt.pie(
            shares,
            explode=explode,
            labels=cities,
            colors=colors,
            autopct='%1.1f%%',
            startangle=140,
            pctdistance=0.85,
            textprops={'fontsize': 9}
        )

        plt.title('Доля вакансий по городам (ТОП-10)', pad=20, fontsize=14, fontweight='bold')

        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')

        for patch in patches:
            patch.set_edgecolor('white')
            patch.set_linewidth(0.5)

        plt.tight_layout()
        output_path = Path(settings.MEDIA_ROOT) / 'charts' / 'vacancy_share_by_city.png'
        plt.savefig(output_path, dpi=CHART_STYLES['dpi'], bbox_inches='tight')
        plt.close()
        logger.info(f"График сохранен: {output_path}")

    except Exception as e:
        logger.error(f"Ошибка генерации vacancy_share_by_city_chart: {str(e)}")
        raise

def generate_top_skills_chart():
    try:
        skills = Skill.objects.filter(is_for_profession=False).order_by('-count')[:20]
        if not skills:
            logger.warning("Нет данных для top_skills_chart")
            return

        skill_names = [skill.name for skill in skills]
        counts = [skill.count for skill in skills]

        plt.figure(figsize=(12, 8))
        bars = plt.barh(
            skill_names[::-1], 
            counts[::-1], 
            color=CHART_STYLES['colors']['general']
        )

        plt.title('ТОП-20 наиболее востребованных навыков', pad=20, fontsize=14, fontweight='bold')
        plt.xlabel('Количество упоминаний', labelpad=10)
        plt.grid(axis='x', linestyle='--', alpha=0.7)

        for bar in bars:
            width = bar.get_width()
            plt.text(
                width, 
                bar.get_y() + bar.get_height()/2., 
                f'{width:,}'.replace(',', ' '),
                ha='left', 
                va='center', 
                fontsize=9, 
                pad=5
            )

        plt.tight_layout()
        output_path = Path(settings.MEDIA_ROOT) / 'charts' / 'top_skills.png'
        plt.savefig(output_path, dpi=CHART_STYLES['dpi'], bbox_inches='tight')
        plt.close()
        logger.info(f"График сохранен: {output_path}")

    except Exception as e:
        logger.error(f"Ошибка генерации top_skills_chart: {str(e)}")
        raise

def generate_all_charts():
    try:
        setup_environment()
        logger.info("Начало генерации графиков...")
        
        generate_salary_by_year_chart()
        generate_vacancies_by_year_chart()
        generate_salary_by_city_chart()
        generate_vacancy_share_by_city_chart()
        generate_top_skills_chart()
        
        logger.info("Все графики успешно сгенерированы!")
    except Exception as e:
        logger.error(f"Критическая ошибка при генерации графиков: {str(e)}")
        raise

if __name__ == '__main__':
    generate_all_charts()