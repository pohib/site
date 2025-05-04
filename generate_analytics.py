import os
import django
import matplotlib.pyplot as plt
import numpy as np
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

def filter_extreme_salaries(salaries):
    return [min(s, MAX_SALARY) if s is not None else None for s in salaries]

def generate_salary_by_year_chart():
    try:
        data = SalaryByYear.objects.all().order_by('year')
        if not data:
            logger.warning("Нет данных для salary_by_year_chart")
            return

        years = [item.year for item in data]
        avg_salaries = filter_extreme_salaries([item.average_salary for item in data])
        prof_salaries = filter_extreme_salaries([item.profession_average_salary for item in data])

        plt.figure(figsize=(14, 7))
        bar_width = 0.35
        index = np.arange(len(years))

        bars1 = plt.bar(
            index - bar_width/2,
            avg_salaries,
            bar_width,
            label='Все вакансии',
            color=CHART_STYLES['colors']['general']
        )

        if any(s for s in prof_salaries if s is not None):
            bars2 = plt.bar(
                index + bar_width/2,
                prof_salaries,
                bar_width,
                label='C# разработчик',
                color=CHART_STYLES['colors']['profession']
            )

        plt.title('Динамика уровня зарплат по годам', pad=20, fontsize=14, fontweight='bold')
        plt.xlabel('Год', labelpad=10)
        plt.ylabel('Средняя зарплата, руб', labelpad=10)
        plt.xticks(index, years)
        plt.gca().yaxis.set_major_formatter(currency_formatter)
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        for bar in bars1:
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

        if 'bars2' in locals():
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
        prof_vacancies = [item.profession_vacancy_count for item in data]

        plt.figure(figsize=CHART_STYLES['figure_size'])

        plt.yscale('log')
        
        line1 = plt.plot(
            years, 
            total_vacancies, 
            'o-', 
            label='Все вакансии', 
            color=CHART_STYLES['colors']['general'], 
            linewidth=2, 
            markersize=8
        )
        
        if any(v for v in prof_vacancies if v):
            line2 = plt.plot(
                years, 
                prof_vacancies, 
                's-', 
                label='C# разработчик', 
                color=CHART_STYLES['colors']['profession'], 
                linewidth=2, 
                markersize=8
            )

        plt.title('Динамика количества вакансий по годам (лог. шкала)', pad=20, fontsize=14, fontweight='bold')
        plt.xlabel('Год', labelpad=10)
        plt.ylabel('Количество вакансий (лог. шкала)', labelpad=10)
        plt.legend()
        plt.grid(True, which="both", linestyle='--', alpha=0.7)

        for x, y in zip(years, total_vacancies):
            plt.text(
                x, y, 
                f'{y:,}'.replace(',', ' '), 
                ha='center', 
                va='bottom', 
                fontsize=9
            )

        if any(v for v in prof_vacancies if v):
            for x, y in zip(years, prof_vacancies):
                if y:
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
        EXCLUDE_COUNTRIES = [
            'австралия', 'австрия', 'азербайджан', 'албания', 'алжир', 
            'ангола', 'андорра', 'антигуа и барбуда', 'аргентина', 'армения',
            'афганистан', 'багамы', 'бангладеш', 'барбадос', 'бахрейн', 'беларусь', 'белиз',
            'бельгия', 'бенин', 'болгария', 'боливия', 'босния и герцеговина', 'ботсвана',
            'бразилия', 'бруней', 'буркина-фасо', 'бурунди', 'бутан', 'вануату', 'ватикан',
            'великобритания', 'венгрия', 'венесуэла', 'восточный тимор', 'вьетнам', 'габон',
            'гаити', 'гамбия', 'гана', 'гватемала', 'гвинея', 'гвинея-бисау', 'германия',
            'гондурас', 'гренада', 'греция', 'грузия', 'дания', 'джибути', 'доминика',
            'доминиканская республика', 'египет', 'замбия', 'зимбабве', 'израиль', 'индия',
            'индонезия', 'иордания', 'ирак', 'иран', 'ирландия', 'исландия', 'испания',
            'италия', 'йемен', 'кабо-верде', 'казахстан', 'камбоджа', 'камерун', 'канада',
            'катар', 'кения', 'кипр', 'киргизия', 'кирибати', 'китай', 'колумбия', 'коморы',
            'конго', 'коста-рика', 'кот-д’ивуар', 'куба', 'кувейт', 'лаос', 'латвия',
            'лесото', 'либерия', 'ливан', 'ливия', 'литва', 'лихтенштейн', 'люксембург',
            'маврикий', 'мавритания', 'мадагаскар', 'малави', 'малайзия', 'мали', 'мальта',
            'маршалловы острова', 'марокко', 'мексика', 'микронезия', 'мозамбик', 'молдова',
            'монако', 'монголия', 'мьянма', 'намибия', 'науру', 'непал', 'нигер', 'нигерия',
            'нидерланды', 'никарагуа', 'новая зеландия', 'норвегия', 'оман', 'пакистан',
            'палау', 'панама', 'папуа — новая гвинея', 'парагвай', 'перу', 'польша',
            'португалия', 'республика корея', 'республика конго', 'россия', 'руанда',
            'румыния', 'сальвадор', 'самоа', 'сан-марино', 'сан-томе и принципе',
            'саудовская аравия', 'северная корея', 'северная македония', 'сейшелы', 'сенгал',
            'сент-винсент и гренадины', 'сент-китс и невис', 'сент-люсия', 'сербия',
            'сингапур', 'сирия', 'словакия', 'словения', 'соединённые штаты америки', 'сомали',
            'судан', 'суринам', 'сьерра-леоне', 'таджикистан', 'таиланд', 'танзания', 'того',
            'тонга', 'тринидад и тобаго', 'тувалу', 'тунис', 'туркменистан', 'турция',
            'уганда', 'узбекистан', 'украина', 'уругвай', 'федеративные штаты микронезии',
            'фиджи', 'филиппины', 'финляндия', 'франция', 'хорватия', 'центральноафриканская республика',
            'чад', 'черногория', 'чехия', 'чили', 'швейцария', 'швеция', 'шри-ланка', 'эквадор',
            'экваториальная гвинея', 'эритрея', 'эсватини', 'эстония', 'эфиопия', 'юар',
            'южный судан', 'ямайка', 'япония',
            'российская федерация', 'республика беларусь', 'княжество монако', 
            'сша', 'америка', 'великобритания', 'соединенное королевство', 'объединенные арабские эмираты',
            'оаэ', 'кнр', 'кыргызстан', 'кот-д’ивуар', 'берег слоновой кости', 'др конго',
            'демократическая республика конго', 'южная корея', 'северная ирландия', 'тайвань',
            'палестина', 'государство палестина', 'макао', 'гонконг', 'бруней-даруссалам',
            'кабо-верде', 'острова кука', 'виргинские острова', 'кюрасао', 'сент-люсия',
            'сейшельские острова', 'тринидад и тобаго', 'антигуа и барбуда', 'сент-китс и невис',
            'сан-томе и принсипи', 'сао-томе и принсипи'
        ]
        
        data_prof = SalaryByCity.objects.filter(
            is_for_profession=True,
            average_salary__isnull=False,
            average_salary__lte=MAX_SALARY
        ).exclude(
            city__iregex=r'^(?!.*\().*$'
        ).exclude(
            city__iregex='|'.join([f'^{country}$' for country in EXCLUDE_COUNTRIES])
        ).order_by('-average_salary')[:10]
        
        if not data_prof:            
            data_prof = SalaryByCity.objects.filter(
                is_for_profession=True,
                average_salary__isnull=False,
                average_salary__lte=MAX_SALARY,
                city__regex=r'^[а-яА-ЯёЁ\-]+$'
            ).exclude(
                city__iregex='|'.join(EXCLUDE_COUNTRIES)
            ).order_by('-average_salary')[:10]
            
            if not data_prof:
                logger.warning("Нет данных по зарплатам C# разработчиков для построения графика")
                return
            
        def clean_city_name(city):
            if '(' in city:
                return city.split('(')[0].strip()
            return city
        
        prof_cities = [clean_city_name(item.city) for item in data_prof]
        original_city_names = [item.city for item in data_prof]
        logger.info(f"Обработанные города: {original_city_names} -> {prof_cities}")
        
        data_all = SalaryByCity.objects.filter(
            is_for_profession=False,
            city__in=original_city_names,
            average_salary__isnull=False,
            average_salary__lte=MAX_SALARY
        ).order_by('-average_salary')
        
        all_salaries_dict = {clean_city_name(item.city): item.average_salary for item in data_all}
        prof_salaries_dict = {clean_city_name(item.city): item.average_salary for item in data_prof}
        
        cities = []
        all_salaries = []
        csharp_salaries = []
        
        for city, original_name in zip(prof_cities, original_city_names):
            if city in all_salaries_dict:
                cities.append(city)
                all_salaries.append(all_salaries_dict[city])
                csharp_salaries.append(prof_salaries_dict[city])
        
        if not cities:
            logger.warning("Нет данных для построения графика")
            return
        
        plt.figure(figsize=(14, 8))
        plt.subplots_adjust(right=0.8)
        
        bar_height = 0.35
        y_pos = np.arange(len(cities))
        
        bars_all = plt.barh(
            y_pos + bar_height/2,
            all_salaries,
            bar_height,
            color=CHART_STYLES['colors']['general'],
            label='Все вакансии'
        )
        
        bars_prof = plt.barh(
            y_pos - bar_height/2,
            csharp_salaries,
            bar_height,
            color=CHART_STYLES['colors']['profession'],
            label='C# разработчик',
            alpha=0.8
        )
            
        plt.yticks(y_pos, cities, fontsize=10)
        plt.title('Сравнение зарплат по городам (ТОП-10 для C# разработчиков)', 
                pad=20, fontsize=14, fontweight='bold')
        plt.xlabel('Средняя зарплата, руб', labelpad=10)
        plt.gca().xaxis.set_major_formatter(currency_formatter)
        plt.grid(axis='x', linestyle='--', alpha=0.5)
        plt.legend(loc='lower right')
        
        max_salary = max(all_salaries + csharp_salaries)
        
        for bars, salaries in [(bars_all, all_salaries), (bars_prof, csharp_salaries)]:
            for bar, salary in zip(bars, salaries):
                text_x = min(salary + 0.02 * max_salary, max_salary * 0.98)
                plt.text(
                    text_x,
                    bar.get_y() + bar.get_height()/2,
                    f'{salary:,.0f}'.replace(',', ' '),
                    va='center',
                    fontsize=9,
                    bbox=dict(facecolor='white', alpha=0.7, pad=1, edgecolor='none')
                )
                        
        plt.tight_layout()
        output_path = Path(settings.MEDIA_ROOT) / 'charts' / 'salary_by_city.png'
        plt.savefig(output_path, dpi=CHART_STYLES['dpi'], bbox_inches='tight')
        plt.close()
        logger.info(f"График успешно сохранен: {output_path}")

    except Exception as e:
        logger.error(f"Ошибка генерации графика: {str(e)}", exc_info=True)
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
        skills = Skill.objects.filter(is_for_profession=True).order_by('-count')[:20]      
        if not skills:
            logger.warning("Нет данных по навыкам для C# разработчиков")
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
                fontsize=9
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