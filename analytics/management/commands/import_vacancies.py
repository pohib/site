import csv
from django.core.management.base import BaseCommand
from analytics.models import SalaryByYear, SalaryByCity, Skill
from datetime import datetime
import os
from django.conf import settings
import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import vacancies data from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to CSV file')

    def handle(self, *args, **options):
        file_path = options['file_path']
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR('File not found'))
            return

        SalaryByYear.objects.all().delete()
        SalaryByCity.objects.all().delete()
        Skill.objects.all().delete()

        year_stats = {}
        city_stats = {}
        skills_stats = {}

        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                name = row['name'].lower()
                if not any(kw in name for kw in ['c#', 'c sharp', 'шарп', 'с#']):
                    continue
                try:
                    pub_date = datetime.strptime(row['published_at'], '%Y-%m-%dT%H:%M:%S%z')
                    year = pub_date.year
                except:
                    continue

                salary_from = float(row['salary_from']) if row['salary_from'] else None
                salary_to = float(row['salary_to']) if row['salary_to'] else None
                currency = row['salary_currency']
                city = row['area_name']

                if year not in year_stats:
                    year_stats[year] = {
                        'total_salaries': [],
                        'prof_salaries': [],
                        'total_vacancies': 0,
                        'prof_vacancies': 0
                    }

                if salary_from is not None and salary_to is not None:
                    avg_salary = (salary_from + salary_to) / 2
                    year_stats[year]['total_salaries'].append(avg_salary)
                    year_stats[year]['prof_salaries'].append(avg_salary)
                else:
                    continue

                year_stats[year]['total_vacancies'] += 1
                year_stats[year]['prof_vacancies'] += 1

                if city not in city_stats:
                    city_stats[city] = {
                        'salaries': [],
                        'vacancies': 0
                    }
                if salary_from is not None and salary_to is not None:
                    city_stats[city]['salaries'].append((salary_from + salary_to) / 2)
                city_stats[city]['vacancies'] += 1
                
        for year, stats in year_stats.items():
            avg_salary = sum(stats['total_salaries'])/len(stats['total_salaries']) if stats['total_salaries'] else 0
            prof_avg = sum(stats['prof_salaries'])/len(stats['prof_salaries']) if stats['prof_salaries'] else 0
            
            SalaryByYear.objects.create(
                year=year,
                average_salary=avg_salary,
                vacancy_count=stats['total_vacancies'],
                profession_average_salary=prof_avg,
                profession_vacancy_count=stats['prof_vacancies']
            )
            
        for city, stats in city_stats.items():
            avg_salary = sum(stats['salaries'])/len(stats['salaries']) if stats['salaries'] else 0
            
            SalaryByCity.objects.create(
                city=city,
                average_salary=avg_salary,
                vacancy_share=(stats['vacancies'] / len(city_stats)) * 100,
                is_for_profession=False
            )
            
        for skill, count in skills_stats.items():
            Skill.objects.create(
                name=skill,
                year=datetime.now().year,
                count=count,
                is_for_profession=True
            )

        self.stdout.write(self.style.SUCCESS('Data imported successfully'))