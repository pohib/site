import os
import django
from django.db import models
import matplotlib.pyplot as plt
import numpy as np
from django.conf import settings
from matplotlib.ticker import FuncFormatter
import logging
from pathlib import Path
from matplotlib import rcParams
from matplotlib import patheffects
import seaborn as sns
from analytics.models import SalaryByYear, SalaryByCity, Skill
import json
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Site.settings')
django.setup()

MAX_SALARY = 10000000

CHART_STYLES = {
    'colors': {
        'general': '#3498db',
        'profession': '#2ecc71',
        'secondary': '#95a5a6',
        'highlight': '#e74c3c',
        'background': '#f9f9f9',
        'text': '#2c3e50',
        'grid': '#ecf0f1'
    },
    'figure_size': (16, 8),
    'dpi': 200,
    'font': {
        'family': 'Arial',
        'title': 18,
        'labels': 14,
        'ticks': 12,
        'legend': 12
    },
    'padding': {
        'default': {
            'left': 0.1,
            'right': 0.9,
            'top': 0.95,
            'bottom': 0.1
        },
        'horizontal': {
            'left': 0.4,
            'right': 0.9,
            'top': 0.95,
            'bottom': 0.1
        },
        'pie': {
            'left': 0.1,
            'right': 0.7,
            'top': 0.95,
            'bottom': 0.1
        }
    }
}

def configure_plot_style():
    sns.set_style("darkgrid")
    rcParams['font.family'] = CHART_STYLES['font']['family']
    rcParams['axes.titlesize'] = CHART_STYLES['font']['title']
    rcParams['axes.labelsize'] = CHART_STYLES['font']['labels']
    rcParams['xtick.labelsize'] = CHART_STYLES['font']['ticks']
    rcParams['ytick.labelsize'] = CHART_STYLES['font']['ticks']
    rcParams['legend.fontsize'] = CHART_STYLES['font']['legend']
    rcParams['figure.facecolor'] = CHART_STYLES['colors']['background']
    rcParams['axes.facecolor'] = CHART_STYLES['colors']['background']
    rcParams['grid.color'] = CHART_STYLES['colors']['grid']
    rcParams['text.color'] = CHART_STYLES['colors']['text']
    rcParams['axes.labelcolor'] = CHART_STYLES['colors']['text']
    rcParams['xtick.color'] = CHART_STYLES['colors']['text']
    rcParams['ytick.color'] = CHART_STYLES['colors']['text']

def setup_environment():
    charts_dir = Path(settings.MEDIA_ROOT) / 'charts'
    charts_dir.mkdir(parents=True, exist_ok=True)
    
    data_dir = Path(settings.MEDIA_ROOT) / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    return charts_dir, data_dir

def format_currency(x, pos):
    return f'{int(x):,}'.replace(',', ' ')

currency_formatter = FuncFormatter(format_currency)

def filter_extreme_salaries(salaries):
    return [min(s, MAX_SALARY) if s is not None else None for s in salaries]

def save_data_to_json(data, filename):
    data_dir = Path(settings.MEDIA_ROOT) / 'data'
    data_dir.mkdir(exist_ok=True, parents=True)
    
    filepath = data_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Данные сохранены в {filepath}")

def get_salary_by_year_data():
    data = SalaryByYear.objects.all().order_by('year')
    result = {
        'years': [item.year for item in data],
        'avg_salaries': [item.average_salary for item in data],
        'prof_salaries': [item.profession_average_salary for item in data],
        'vacancy_counts': [item.vacancy_count for item in data],
        'prof_vacancy_counts': [item.profession_vacancy_count for item in data],
    }
    save_data_to_json(result, 'salary_by_year.json')
    return result

def get_salary_by_city_data():
    EXCLUDE_COUNTRIES = [
            'австралия', 'австрия', 'азербайджан', 'албания', 'алжир', 
            'ангола', 'андорра', 'антигуа и барбуда', 'аргентина', 'армения',
            'афганистан', 'абхазия', 'багамы', 'бангладеш', 'барбадос', 'бахрейн', 'беларусь', 'белиз',
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
            'сан-томе и принсипи', 'сао-томе и принсипи', 'текели'
    ]

    data_prof = SalaryByCity.objects.filter(
        is_for_profession=True,
        average_salary__isnull=False,
        average_salary__lte=MAX_SALARY
    ).exclude(
        city__iregex=r'^(?:{})$'.format('|'.join(EXCLUDE_COUNTRIES))
    ).order_by('-average_salary')

    def clean_city_name(city):
        return city.split('(')[0].strip().lower()

    city_groups = {}
    for item in data_prof:
        clean_city = clean_city_name(item.city)
        if clean_city not in city_groups:
            city_groups[clean_city] = {
                'original_names': [item.city],
                'salaries': [item.average_salary],
            }
        else:
            city_groups[clean_city]['original_names'].append(item.city)
            city_groups[clean_city]['salaries'].append(item.average_salary)

    prof_salaries_dict = {
        city: sum(data['salaries']) / len(data['salaries'])
        for city, data in city_groups.items()
    }

    top_cities = sorted(
        prof_salaries_dict.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    original_city_names = [
        city_groups[city]['original_names'][0]
        for city, _ in top_cities
    ]

    data_all = SalaryByCity.objects.filter(
        is_for_profession=False,
        city__in=original_city_names,
        average_salary__isnull=False,
        average_salary__lte=MAX_SALARY
    )

    all_salaries_dict = {}
    for item in data_all:
        clean_city = clean_city_name(item.city)
        if clean_city not in all_salaries_dict:
            all_salaries_dict[clean_city] = [item.average_salary]
        else:
            all_salaries_dict[clean_city].append(item.average_salary)

    all_salaries_dict = {
        city: sum(salaries) / len(salaries)
        for city, salaries in all_salaries_dict.items()
    }

    result = {
        'cities': [city for city, _ in top_cities],
        'all_salaries': [all_salaries_dict.get(city, 0) for city, _ in top_cities],
        'csharp_salaries': [salary for _, salary in top_cities],
        'original_city_names': original_city_names,
    }

    save_data_to_json(result, 'salary_by_city.json')
    return result

def get_vacancy_share_by_city_data():
    data = SalaryByCity.objects.filter(is_for_profession=True).order_by('-vacancy_share')[:10]
    result = {
        'cities': [item.city for item in data],
        'shares': [item.vacancy_share for item in data],
        'vacancy_counts': [item.vacancy_share for item in data]
    }
    save_data_to_json(result, 'vacancy_share_by_city.json')
    return result

def get_top_skills_data():
    def normalize_skill_name(name):
        name = name.strip().lower()
        if name.startswith('с#'):
            name = 'c#' + name[2:]
            
        replacements = {
            '.net framework': '.net',
            'asp.net core': 'asp.net',
            'ms sql': 'sql server',
            'postgresql': 'postgres'
        }
        
        for old, new in replacements.items():
            if name == old:
                name = new
                break
        return name
    
    all_skills = Skill.objects.filter(is_for_profession=True)        
    skills_agg = {}
    
    for skill in all_skills:
        original_name = skill.name.strip()
        normalized_name = normalize_skill_name(original_name)
        
        if normalized_name in skills_agg:
            if skill.count > skills_agg[normalized_name]['count']:
                skills_agg[normalized_name] = {
                    'display_name': original_name,
                    'count': skill.count,
                    'year': skill.year
                }
        else:
            skills_agg[normalized_name] = {
                'display_name': original_name,
                'count': skill.count,
                'year': skill.year
            }
    
    top_skills = sorted(skills_agg.values(), 
                    key=lambda x: x['count'], 
                    reverse=True)
    
    skills_by_year = defaultdict(list)
    for skill in Skill.objects.filter(is_for_profession=True):
        normalized_name = normalize_skill_name(skill.name)
        if normalized_name in [s['display_name'].lower() for s in top_skills]:
            skills_by_year[skill.year].append({
                'name': skill.name,
                'count': skill.count
            })
    
    result = {
        'top_skills': top_skills,
        'top_20_skills': top_skills[:20],
        'skills_by_year': skills_by_year
    }
    save_data_to_json(result, 'top_skills.json')
    return result

def generate_salary_by_year_chart():
    try:
        configure_plot_style()
        data = get_salary_by_year_data()
        
        if not data['years']:
            logger.warning("Нет данных для salary_by_year_chart")
            return

        years = data['years']
        avg_salaries = filter_extreme_salaries(data['avg_salaries'])
        prof_salaries = filter_extreme_salaries(data['prof_salaries'])

        fig, ax = plt.subplots(figsize=CHART_STYLES['figure_size'])
        plt.subplots_adjust(**CHART_STYLES['padding']['default'])
        
        bar_width = 0.35
        index = np.arange(len(years))
        
        general_color = [CHART_STYLES['colors']['general']] * len(years)
        profession_color = [CHART_STYLES['colors']['profession']] * len(years)

        bars1 = ax.bar(
            index - bar_width/2,
            avg_salaries,
            bar_width,
            label='Все вакансии',
            color=general_color,
            edgecolor='white',
            linewidth=1,
            alpha=0.9
        )

        if any(s for s in prof_salaries if s is not None):
            bars2 = ax.bar(
                index + bar_width/2,
                prof_salaries,
                bar_width,
                label='C# разработчик',
                color=profession_color,
                edgecolor='white',
                linewidth=1,
                alpha=0.9
            )
            
        for bars in [bars1, bars2] if 'bars2' in locals() else [bars1]:
            for bar in bars:
                bar.set_path_effects([
                    patheffects.withStroke(
                        linewidth=2, foreground='black', alpha=0.1
                    )
                ])

        ax.set_title('Динамика уровня зарплат по годам', 
                pad=20,
                fontsize=16,
                fontweight='bold',
                color=CHART_STYLES['colors']['text'])
        
        ax.set_xlabel('Год', labelpad=15)
        ax.set_ylabel('Средняя зарплата, руб', labelpad=15)
        ax.set_xticks(index)
        ax.set_xticklabels(years)
        ax.yaxis.set_major_formatter(currency_formatter)
        
        ax.legend(
            frameon=True,
            framealpha=0.9,
            facecolor=CHART_STYLES['colors']['background'],
            edgecolor=CHART_STYLES['colors']['grid'],
            bbox_to_anchor=(0, 1),
            loc='upper left'
        )
        
        for bars in [bars1, bars2] if 'bars2' in locals() else [bars1]:
            for bar in bars:
                height = bar.get_height()
                if height:
                    if height > max(avg_salaries + prof_salaries) * 0.8:
                        va = 'top'
                        y_pos = height * 0.98
                    else:
                        va = 'bottom'
                        y_pos = height * 1.02
                    ax.text(
                        bar.get_x() + bar.get_width()/2., 
                        height,
                        f'{height:,.0f}'.replace(',', ' '),
                        ha='center', 
                        va=va,
                        fontsize=8,
                        bbox=dict(
                            facecolor='white',
                            alpha=0.8,
                            edgecolor='none',
                            boxstyle='round,pad=0.2'
                        )
                    )
                    
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(CHART_STYLES['colors']['grid'])
        ax.spines['bottom'].set_color(CHART_STYLES['colors']['grid'])
        
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
        configure_plot_style()
        data = get_salary_by_year_data()
        
        if not data['years']:
            logger.warning("Нет данных для vacancies_by_year_chart")
            return

        years = data['years']
        total_vacancies = data['vacancy_counts']
        prof_vacancies = data['prof_vacancy_counts']
        
        fig, ax = plt.subplots(figsize=CHART_STYLES['figure_size'])
        plt.subplots_adjust(**CHART_STYLES['padding']['default'])
        ax.set_yscale('log')
        
        line1 = ax.plot(
            years, 
            total_vacancies, 
            'o-', 
            label='Все вакансии', 
            color=CHART_STYLES['colors']['general'], 
            linewidth=3, 
            markersize=10,
            markerfacecolor='white',
            markeredgewidth=2
        )
        
        if any(v for v in prof_vacancies if v):
            line2 = ax.plot(
                years, 
                prof_vacancies, 
                's-', 
                label='C# разработчик', 
                color=CHART_STYLES['colors']['profession'], 
                linewidth=3, 
                markersize=10,
                markerfacecolor='white',
                markeredgewidth=2
            )

        ax.set_title('Динамика количества вакансий по годам (лог. шкала)', 
                pad=20, 
                fontweight='bold',
                color=CHART_STYLES['colors']['text'])
        ax.set_xlabel('Год', labelpad=15)
        ax.set_ylabel('Количество вакансий (лог. шкала)', labelpad=15)
        
        ax.legend(
            frameon=True,
            framealpha=0.9,
            facecolor=CHART_STYLES['colors']['background'],
            edgecolor=CHART_STYLES['colors']['grid']
        )
        
        for x, y in zip(years, total_vacancies):
            ax.text(
                x, y * 1.4, 
                f'{y:,}'.replace(',', ' '), 
                ha='center', 
                va='bottom', 
                fontsize=10,
                bbox=dict(
                    facecolor='white',
                    alpha=0.8,
                    edgecolor='none',
                    boxstyle='round,pad=0.2'
                )
            )

        if any(v for v in prof_vacancies if v):
            for x, y in zip(years, prof_vacancies):
                if y:
                    ax.text(
                        x, y * 1.4, 
                        f'{y:,}'.replace(',', ' '), 
                        ha='center', 
                        va='bottom', 
                        fontsize=10,
                        bbox=dict(
                            facecolor='white',
                            alpha=0.8,
                            edgecolor='none',
                            boxstyle='round,pad=0.2'
                        )
                    )
                    
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(CHART_STYLES['colors']['grid'])
        ax.spines['bottom'].set_color(CHART_STYLES['colors']['grid'])
        
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
        configure_plot_style()
        data = get_salary_by_city_data()
        
        if not data['cities']:
            logger.warning("Нет данных для построения графика")
            return
        
        cities = data['cities']
        all_salaries = data['all_salaries']
        csharp_salaries = data['csharp_salaries']
        
        fig, ax = plt.subplots(figsize=CHART_STYLES['figure_size'])
        plt.subplots_adjust(**CHART_STYLES['padding']['default'])
        
        bar_height = 0.35
        y_pos = np.arange(len(cities))
        
        general_color = [CHART_STYLES['colors']['general']] * len(cities)
        profession_color = [CHART_STYLES['colors']['profession']] * len(cities)
        
        bars_all = ax.barh(
            y_pos + bar_height/2,
            all_salaries,
            bar_height,
            color=general_color,
            label='Все вакансии',
            edgecolor='white',
            linewidth=1,
            alpha=0.9
        )
        
        bars_prof = ax.barh(
            y_pos - bar_height/2,
            csharp_salaries,
            bar_height,
            color=profession_color,
            label='C# разработчик',
            edgecolor='white',
            linewidth=1,
            alpha=0.9
        )
            
        ax.set_yticks(y_pos)
        ax.set_yticklabels(cities, fontsize=CHART_STYLES['font']['ticks'])
        ax.set_title('Сравнение зарплат по городам (ТОП-10 для C# разработчиков)', 
                pad=20, 
                fontweight='bold',
                color=CHART_STYLES['colors']['text'])
        ax.set_xlabel('Средняя зарплата, руб', labelpad=15)
        ax.xaxis.set_major_formatter(currency_formatter)
        
        ax.legend(
            frameon=True,
            framealpha=0.9,
            facecolor=CHART_STYLES['colors']['background'],
            edgecolor=CHART_STYLES['colors']['grid'],
            bbox_to_anchor=(1.05, 1),
            loc='upper left'
        )
        
        max_salary = max(all_salaries + csharp_salaries)
        for bars, salaries in [(bars_all, all_salaries), (bars_prof, csharp_salaries)]:
            for bar, salary in zip(bars, salaries):
                text_x = min(salary + 0.02 * max_salary, max_salary * 0.98)
                ax.text(
                    text_x,
                    bar.get_y() + bar.get_height()/2,
                    f'{salary:,.0f}'.replace(',', ' '),
                    va='center',
                    fontsize=10,
                    bbox=dict(
                        facecolor='white',
                        alpha=0.8,
                        edgecolor='none',
                        boxstyle='round,pad=0.2'
                    )
                )
                
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(CHART_STYLES['colors']['grid'])
        ax.spines['bottom'].set_color(CHART_STYLES['colors']['grid'])
        ax.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()
        output_path = Path(settings.MEDIA_ROOT) / 'charts' / 'salary_by_city.png'
        plt.savefig(output_path, dpi=CHART_STYLES['dpi'], bbox_inches='tight')
        plt.close()
        logger.info(f"График сохранен: {output_path}")

    except Exception as e:
        logger.error(f"Ошибка генерации графика: {str(e)}", exc_info=True)
        raise
    
def generate_vacancy_share_by_city_chart():
    try:
        configure_plot_style()
        data = get_vacancy_share_by_city_data()
        
        if not data['cities']:
            logger.warning("Нет данных для vacancy_share_by_city_chart")
            return
        
        cities = data['cities']
        shares = data['shares']
        explode = [0.1] + [0]*(len(cities)-1)
        
        fig, ax = plt.subplots(figsize=CHART_STYLES['figure_size'])
        plt.subplots_adjust(**CHART_STYLES['padding']['pie'])
        
        colors = sns.color_palette("husl", len(cities))
        
        wedges, texts, autotexts = ax.pie(
            shares,
            explode=explode,
            labels=None,
            colors=colors,
            autopct=lambda p: f'{p:.1f}%' if p >= 3 else '',
            startangle=140,
            pctdistance=0.8,
            textprops={
                'fontsize': 12,
                'fontweight': 'bold',
                'color': 'white'
            },
            wedgeprops={
                'edgecolor': 'white',
                'linewidth': 2,
                'alpha': 0.9
            }
        )
        
        ax.set_title('Доля вакансий по городам (ТОП-10)', 
                y=1.05,
                x=0.65,
                fontsize=18,
                fontweight='bold')
        
        legend = ax.legend(
            wedges,
            [f"{city} ({share:.1f}%)" for city, share in zip(cities, shares)],
            title="Города",
            loc="center left",           
            bbox_to_anchor=(1, 0.5),
            fontsize=12,
            title_fontsize=14,
            frameon=False
        )
        
        legend._legend_box.sep = 15
        
        for text in legend.get_texts():
            text.set_fontweight('bold')
            
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
        configure_plot_style()
        data = get_top_skills_data()
        
        if not data.get('skills_by_year'):
            logger.warning("Нет данных по навыкам для C# разработчиков")
            return

        for year, skills in data['skills_by_year'].items():
            top_skills = sorted(skills, key=lambda x: x['count'], reverse=True)[:20]
            
            if not top_skills:
                logger.warning(f"Нет данных по навыкам за {year} год")
                continue

            skill_names = [skill['name'] for skill in top_skills]
            counts = [skill['count'] for skill in top_skills]

            fig, ax = plt.subplots(figsize=(15, 6))
            plt.subplots_adjust(**CHART_STYLES['padding']['horizontal'])
            
            bar_color = CHART_STYLES['colors']['general']
            text_color = CHART_STYLES['colors']['text']

            bars = ax.barh(
                skill_names[::-1],
                counts[::-1],
                color=bar_color,
                edgecolor='white',
                linewidth=1,
                alpha=0.9,
                height=0.7
            )

            ax.set_title(
                f'ТОП-20 наиболее востребованных навыков ({year} год)',
                pad=20,
                fontsize=16,
                fontweight='bold',
                color=text_color
            )

            ax.set_xlabel(
                'Количество упоминаний',
                labelpad=15,
                fontsize=14,
                color=text_color
            )

            ax.set_ylim(-0.5, len(skill_names)-0.5)

            max_count = max(counts) if counts else 0
            for bar in bars:
                width = bar.get_width()
                ax.text(
                    width + (max_count * 0.02),
                    bar.get_y() + bar.get_height()/2.,
                    f'{int(width):,}'.replace(',', ' '),
                    ha='left',
                    va='center',
                    fontsize=12,
                    fontweight='bold',
                    color=text_color
                )

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_alpha(0.3)

            ax.grid(axis='x', linestyle='--', alpha=0.3)
            ax.set_axisbelow(True)

            ax.tick_params(axis='y', labelsize=11, colors=text_color)
            ax.tick_params(axis='x', colors=text_color)

            plt.tight_layout()
            output_path = Path(settings.MEDIA_ROOT) / 'charts' / f'top_skills_{year}.png'
            plt.savefig(output_path, dpi=CHART_STYLES['dpi'], bbox_inches='tight')
            plt.close()
            logger.info(f"График для {year} года сохранен: {output_path}")

    except Exception as e:
        logger.error(f"Ошибка генерации top_skills_chart: {str(e)}")
        raise


def generate_all_charts():
    try:
        charts_dir, data_dir = setup_environment()
        logger.info("Начало генерации графиков и данных...")
        
        generate_salary_by_year_chart()
        generate_vacancies_by_year_chart()
        generate_salary_by_city_chart()
        generate_vacancy_share_by_city_chart()
        generate_top_skills_chart()
        
        logger.info("Все графики и данные успешно сгенерированы!")
    except Exception as e:
        logger.error(f"Критическая ошибка при генерации графиков и данных: {str(e)}")
        raise

if __name__ == '__main__':
    generate_all_charts()