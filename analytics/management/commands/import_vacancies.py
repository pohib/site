import time
import csv
from django.core.management.base import BaseCommand
from analytics.models import SalaryByYear, SalaryByCity, Skill
from datetime import datetime, timedelta
import os
from django.conf import settings
import logging
from collections import defaultdict
from tqdm import tqdm
import re
import requests
from decimal import Decimal, getcontext
import math
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)
getcontext().prec = 6

class Command(BaseCommand):
    help = 'Import vacancies data from CSV file with daily currency conversion'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to CSV file')
        parser.add_argument('--max-salary', type=int, default=10000000, help='Maximum allowed salary')
        
    def get_historical_currency_rates(self, date):
        try:
            date_str = date.strftime('%d/%m/%Y')
            url = f"http://www.cbr.ru/scripts/XML_daily.asp?date_req={date_str}"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            root = ET.fromstring(response.content)
            rates = {
                'RUR': Decimal('1.0'),
                'RUB': Decimal('1.0'),
            }
            
            currency_codes = {
                'USD': 'R01235',
                'EUR': 'R01239',
                'KZT': 'R01335',
                'BYN': 'R01090B',
                'BYR': 'R01090',
            }
            
            for valute in root.findall('Valute'):
                valute_id = valute.get('ID')
                charcode = valute.find('CharCode').text
                nominal = Decimal(valute.find('Nominal').text)
                value = Decimal(valute.find('Value').text.replace(',', '.'))
                
                rates[charcode] = value / nominal
                
                if valute_id == currency_codes['BYR']:
                    rates['BYR'] = value / nominal
                elif valute_id == currency_codes['BYN']:
                    rates['BYN'] = value / nominal
            
            logger.debug(f"Курсы валют на {date_str}: {rates}")
            return rates
            
        except Exception as e:
            logger.warning(f"Не удалось получить курсы на {date_str}: {e}")
            return None
        
    def get_monthly_currency_rates(self, year_month):
        
        first_day = datetime.strptime(year_month + '-01', '%Y-%m-%d').date()
        
        for days_back in range(0, 10):
            current_date = first_day - timedelta(days=days_back)
            rates = self.get_historical_currency_rates(current_date)
            if rates is not None:
                logger.info(f"Используем курсы за {current_date.strftime('%d.%m.%Y')} для месяца {year_month}")
                return rates
                
        logger.warning(f"Не удалось получить курсы для {year_month}, используются резервные значения")
        return {
            'USD': Decimal('75.0'),
            'EUR': Decimal('85.0'),
            'KZT': Decimal('0.2'),
            'BYN': Decimal('28.5'),
            'BYR': Decimal('0.00285'),
            'RUR': Decimal('1.0'),
            'RUB': Decimal('1.0'),
        }
        
    def convert_salary(self, salary, currency, rates):
        
        if salary is None or math.isnan(salary) or salary <= 0:
            return None
            
        currency = currency.upper().strip()
        
        if currency not in rates:
            logger.debug(f"Неподдерживаемая валюта: {currency}")
            return None
            
        try:
            return float(Decimal(salary) * rates[currency])
        except Exception as e:
            logger.warning(f"Ошибка конвертации зарплаты {salary} {currency}: {e}")
            return None
        
    def handle(self, *args, **options):
        file_path = options['file_path']
        max_salary = options['max_salary']
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR('Файл не найден'))
            return
        
        rates_cache = {}
        
        self.initialize_import()
        self.process_file(file_path, rates_cache, max_salary)
        self.save_results()
        
    def initialize_import(self):
        
        self.stdout.write("Очистка старых данных...")
        SalaryByYear.objects.all().delete()
        SalaryByCity.objects.all().delete()
        Skill.objects.all().delete()
        
        self.year_stats = defaultdict(lambda: {
            'total_salaries': [],
            'prof_salaries': [],
            'total_vacancies': 0,
            'prof_vacancies': 0
        })
        
        self.city_stats = defaultdict(lambda: {
            'all_salaries': [],
            'prof_salaries': [],
            'all_vacancies': 0,
            'prof_vacancies': 0
        })
        
        self.skills_stats = defaultdict(int)
        self.all_skills_stats = defaultdict(int)
        
    def process_file(self, file_path, rates_cache, max_salary):
        
        with open(file_path, mode='r', encoding='utf-8') as file:
            total_rows = sum(1 for _ in file) - 1
            
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            processed_rows = 0
            skipped_rows = 0
                        
            for row in tqdm(reader, total=total_rows, desc="Обработка вакансий"):
                try:
                    if not self.process_vacancy(row, rates_cache, max_salary):
                        skipped_rows += 1
                    processed_rows += 1
                except Exception as e:
                    logger.warning(f"Ошибка обработки вакансии: {e}")
                    skipped_rows += 1
                    
            logger.info(f"Обработано строк: {processed_rows}, пропущено: {skipped_rows}")
            
    def process_vacancy(self, row, rates_cache, max_salary):
        
        try:
            pub_date = datetime.strptime(row['published_at'], '%Y-%m-%dT%H:%M:%S%z')
            year = pub_date.year
            year_month = pub_date.strftime('%Y-%m')
            
            if year_month not in rates_cache:
                rates_cache[year_month] = self.get_monthly_currency_rates(year_month)
            rates = rates_cache[year_month]
        except Exception as e:
            logger.debug(f"Не удалось распарсить дату публикации: {e}")
            return False
        
        try:
            salary_from = float(row['salary_from']) if row['salary_from'] else None
            salary_to = float(row['salary_to']) if row['salary_to'] else None
            currency = row['salary_currency'].strip().upper()
        except Exception as e:
            logger.debug(f"Не удалось распарсить зарплату: {e}")
            return False
        
        salary_from_rub = self.convert_salary(salary_from, currency, rates)
        salary_to_rub = self.convert_salary(salary_to, currency, rates)
        
        if salary_from_rub and salary_from_rub > max_salary:
            salary_from_rub = None
        if salary_to_rub and salary_to_rub > max_salary:
            salary_to_rub = None
            
        city = row['area_name'].strip()
        name = row['name'].lower()
        skills = [s.strip() for s in row['key_skills'].split('\n')] if row['key_skills'] else []
        
        is_csharp = bool(re.search(r'c[-\s]?#|с\#|шарп|csharp', name, re.I))       
        
        for skill in skills:
            if skill:
                self.all_skills_stats[(skill, year)] += 1
                if is_csharp:
                    self.skills_stats[(skill, year)] += 1
                    
                    
        avg_salary = None
        if salary_from_rub is not None and salary_to_rub is not None:
            avg_salary = (salary_from_rub + salary_to_rub) / 2
        elif salary_from_rub is not None:
            avg_salary = salary_from_rub
        elif salary_to_rub is not None:
            avg_salary = salary_to_rub
            
        if avg_salary is not None:
            self.year_stats[year]['total_salaries'].append(avg_salary)
            self.city_stats[city]['all_salaries'].append(avg_salary)
            if is_csharp:
                self.year_stats[year]['prof_salaries'].append(avg_salary)
                self.city_stats[city]['prof_salaries'].append(avg_salary)
                
        self.year_stats[year]['total_vacancies'] += 1
        self.city_stats[city]['all_vacancies'] += 1
        if is_csharp:
            self.year_stats[year]['prof_vacancies'] += 1
            self.city_stats[city]['prof_vacancies'] += 1
            
        return True
    
    def save_results(self):
        try:
            self.save_year_stats()
            self.save_city_stats()
            self.save_skills()
            
            self.stdout.write(self.style.SUCCESS('Данные успешно импортированы'))
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных: {str(e)}")
            self.stdout.write(self.style.ERROR(f'Ошибка: {str(e)}'))
            
    def save_year_stats(self):
        self.stdout.write("Сохранение статистики по годам...")
        
        objects = []
        for year, stats in tqdm(self.year_stats.items(), desc="Years"):
            avg_salary = sum(stats['total_salaries'])/len(stats['total_salaries']) if stats['total_salaries'] else None
            prof_avg_salary = sum(stats['prof_salaries'])/len(stats['prof_salaries']) if stats['prof_salaries'] else None
            
            if avg_salary is not None:
                objects.append(
                    SalaryByYear(
                        year=year,
                        average_salary=avg_salary,
                        vacancy_count=stats['total_vacancies'],
                        profession_average_salary=prof_avg_salary,
                        profession_vacancy_count=stats['prof_vacancies']
                    )
                )
        
        SalaryByYear.objects.bulk_create(objects, batch_size=1000)
        
    def save_city_stats(self):
        self.stdout.write("Сохранение статистики по городам...")
        
        total_all_vacancies = sum(city['all_vacancies'] for city in self.city_stats.values())
        total_prof_vacancies = sum(city['prof_vacancies'] for city in self.city_stats.values())
        
        city_objects = []
        processed_cities = set()
        
        for city in tqdm(self.city_stats.keys(), desc="Получение координат"):
            if city not in processed_cities:
                lat, lon = self.get_city_coordinates(city)
                processed_cities.add(city)
        
        for city, stats in tqdm(self.city_stats.items(), desc="Создание объектов"):
            lat, lon = self.get_city_coordinates(city)
            
            if stats['all_salaries']:
                avg_salary = sum(stats['all_salaries'])/len(stats['all_salaries'])
                share = (stats['all_vacancies']/total_all_vacancies)*100 if total_all_vacancies else 0
                
                city_objects.append(
                    SalaryByCity(
                        city=city,
                        average_salary=avg_salary,
                        vacancy_share=share,
                        is_for_profession=False,
                        lat=lat,
                        lon=lon
                    )
                )
                
            if stats['prof_vacancies'] > 0 and stats['prof_salaries']:
                avg_salary = sum(stats['prof_salaries'])/len(stats['prof_salaries'])
                share = (stats['prof_vacancies']/total_prof_vacancies)*100 if total_prof_vacancies else 0
                
                city_objects.append(
                    SalaryByCity(
                        city=city,
                        average_salary=avg_salary,
                        vacancy_share=share,
                        is_for_profession=True,
                        lat=lat,
                        lon=lon
                    )
                )
        SalaryByCity.objects.bulk_create(city_objects, batch_size=1000)
            
            
    def save_skills(self):
        self.stdout.write("Сохранение навыков...")
        
        Skill.objects.bulk_create([
            Skill(
                name=skill,
                year=year,
                count=count,
                is_for_profession=False
            ) for (skill, year), count in tqdm(self.all_skills_stats.items(), desc="All skills")
            if count > 0 
        ], batch_size=1000)
        
        Skill.objects.bulk_create([
            Skill(
                name=skill,
                year=year,
                count=count,
                is_for_profession=True
            ) for (skill, year), count in tqdm(self.skills_stats.items(), desc="Profession skills")
            if count > 0
        ], batch_size=1000)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.yandex_api_key = "25e17625-2184-4bea-bd71-15e9f532b772"
        self.geocoder_url = "https://geocode-maps.yandex.ru/1.x/"
        self.coordinates_cache = {}
        self.request_delay = 0.2
        self.last_request_time = 0
        
    def get_city_coordinates(self, city_name):
        if not city_name:
            return None, None
        
        if city_name in self.coordinates_cache:
            return self.coordinates_cache[city_name]
        
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
            
        try:
            params = {
                'geocode': city_name,
                'format': 'json',
                'apikey': self.yandex_api_key,
                'results': 1,
                'kind': 'locality'
            }

            response = requests.get(self.geocoder_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            features = data.get('response', {}).get('GeoObjectCollection', {}).get('featureMember', [])
            if not features:
                logger.debug(f"Город не найден: {city_name}")
                return None, None
                
            geo_object = features[0]['GeoObject']
            pos = geo_object['Point']['pos']
            lon, lat = map(float, pos.split())
            
            self.coordinates_cache[city_name] = (lat, lon)
            self.last_request_time = time.time()
            self.coordinates_cache[city_name] = (lat, lon) 
            
            logger.debug(f"Найдены координаты для {city_name}: {lat}, {lon}")
            return lat, lon
            
        except Exception as e:
            logger.warning(f"Ошибка геокодирования для {city_name}: {e}")
            self.coordinates_cache[city_name] = (None, None)
            return None, None