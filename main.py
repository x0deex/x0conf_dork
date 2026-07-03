#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
x0conf_dork - инструмент для создания поисковых запросов (дорков)
для поиска информации о человеке в интернете.
"""

import sys
import urllib.parse
import webbrowser
from typing import List, Dict, Optional

# ========================== ПОДДЕРЖКА ЦВЕТОВ В CMD ==========================
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN
    RESET = Fore.RESET
    BOLD = Style.BRIGHT
except ImportError:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"

def colored(text: str, color: str = RESET, bold: bool = False) -> str:
    style = BOLD if bold else ""
    return f"{style}{color}{text}{RESET}"

# ========================== ASCII-АРТ ==========================
def print_ascii_art():
    art = r"""
       __               __    _         _   
 __ __/  \ __ ___ _ _  / _|__| |___ _ _| |__
 \ \ / () / _/ _ \ ' \|  _/ _` / _ \ '_| / /
 /_\_\\__/\__\___/_||_|_|_\__,_\___/_| |_\_\
                       |___|                
    """
    print(colored(art, RED, bold=True))

# ========================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========================

def quote(s: str) -> str:
    return urllib.parse.quote(s, safe='')

def make_google_url(query: str) -> str:
    return f"https://www.google.com/search?q={quote(query)}"

def print_queries(queries: List[str], show_google: bool = True):
    if not queries:
        print("Запросы не сгенерированы.")
        return
    for idx, q in enumerate(queries, 1):
        print(f"{colored(str(idx), GREEN, bold=True)}. {q}")
        if show_google:
            print(f"   Google: {colored(make_google_url(q), BLUE)}")
    print()

# ========================== ГЕНЕРАТОРЫ ЗАПРОСОВ ==========================
# (все генераторы остаются без изменений, их полный код приведён ниже)
def gen_profiles(params: Dict[str, str]) -> List[str]:
    name = params.get('name', '')
    if not name:
        return []
    sites = [
        'vk.com', 'ok.ru', 'telegram.me OR site:t.me', 'instagram.com',
        'facebook.com', 'linkedin.com'
    ]
    queries = []
    for site in sites:
        if 'OR' in site:
            queries.append(f'"{name}" site:{site}')
        else:
            queries.append(f'"{name}" site:{site}')
    queries.append(f'inurl:"telegram.me/joinchat" "{name}"')
    queries.append(f'inurl:"instagram.com" intitle:"{name}"')
    queries.append(f'inurl:"facebook.com" "{name}"')
    queries.append(f'intitle:"{name}" site:linkedin.com')
    return queries

def gen_email(params: Dict[str, str]) -> List[str]:
    email = params.get('email', '')
    if not email:
        return []
    local = email.split('@')[0] if '@' in email else email
    domain = email.split('@')[1] if '@' in email else ''
    queries = []
    queries.append(f'"{email}"')
    queries.append(f'"{local}" filetype:xls OR filetype:csv')
    queries.append(f'"{local}" site:pastebin.com')
    queries.append(f'"{local}" site:leakforum.org')
    queries.append(f'"{local}" site:haveibeenpwned.com')
    queries.append(f'"{local}" site:scylla.so')
    if domain:
        queries.append(f'"@{domain}" filetype:xls OR filetype:csv')
    queries.append(f'intext:"email" AND "password" filetype:xls')
    return queries

def gen_phone(params: Dict[str, str]) -> List[str]:
    phone = params.get('phone', '')
    if not phone:
        return []
    queries = []
    queries.append(f'"{phone}"')
    if phone.startswith('+'):
        no_plus = phone[1:]
        queries.append(f'"{no_plus}"')
    else:
        queries.append(f'"+{phone}"')
    queries.append(f'"{phone}" site:vk.com')
    queries.append(f'"{phone}" site:telegram.me')
    queries.append(f'intext:"{phone}"')
    queries.append(f'"{phone}" filetype:txt OR filetype:xls')
    queries.append(f'inurl:"phone" "{phone}"')
    return queries

def gen_docs(params: Dict[str, str]) -> List[str]:
    name = params.get('name', '')
    if not name:
        return []
    queries = []
    for ext in ['pdf', 'doc', 'docx', 'xls']:
        queries.append(f'"{name}" filetype:{ext}')
    queries.append(f'intitle:"Резюме {name}"')
    queries.append(f'intitle:"Curriculum Vitae {name}"')
    queries.append(f'intext:"Опыт работы" "{name}"')
    return queries

def gen_photos(params: Dict[str, str]) -> List[str]:
    name = params.get('name', '')
    if not name:
        return []
    queries = []
    queries.append(f'inurl:uploads "{name}"')
    queries.append(f'inurl:photos "{name}"')
    queries.append(f'"{name}" filetype:jpg OR filetype:png')
    queries.append(f'"{name}" site:imgur.com')
    return queries

def gen_forums(params: Dict[str, str]) -> List[str]:
    name = params.get('name', '')
    if not name:
        return []
    sites = ['4pda.ru', 'habr.com', 'stackoverflow.com']
    queries = []
    for site in sites:
        queries.append(f'"{name}" site:{site}')
    queries.append(f'intext:"{name}" "комментарий"')
    queries.append(f'inurl:"user" "{name}"')
    return queries

def gen_leaks(params: Dict[str, str]) -> List[str]:
    name = params.get('name', '')
    queries = []
    queries.append('filetype:xls intext:"password"')
    queries.append('filetype:txt intext:"login" intext:"password"')
    queries.append('intitle:"index of" "backup"')
    queries.append('intitle:"index of" "database"')
    queries.append('inurl:"db_backup" OR inurl:"backup"')
    queries.append('inurl:"passwords" OR inurl:"credentials"')
    if name:
        queries.append(f'"{name}" filetype:sql')
    return queries

def gen_geo(params: Dict[str, str]) -> List[str]:
    name = params.get('name', '')
    city = params.get('city', '')
    company = params.get('company', '')
    if not name:
        return []
    queries = []
    if city:
        queries.append(f'"{name}" "{city}"')
        if 'Москва' in city or 'Питер' in city:
            queries.append(f'"{name}" "{city}"')
        else:
            queries.append(f'"{name}" "{city}" OR "{city}"')
    if company:
        queries.append(f'"{name}" "работает в" "{company}"')
        queries.append(f'site:linkedin.com "{name}" "{company}"')
        queries.append(f'site:vk.com "{name}" "работа"')
    if not city and not company:
        queries.append(f'"{name}" "Санкт-Петербург"')
        queries.append(f'"{name}" "Москва" OR "Питер"')
    return queries

def gen_admin(params: Dict[str, str]) -> List[str]:
    name = params.get('name', '')
    queries = []
    queries.append('intitle:"login" OR intitle:"вход"')
    queries.append('inurl:"admin"')
    queries.append('inurl:"dashboard"')
    if name:
        queries.append(f'inurl:"user" "{name}"')
        queries.append(f'inurl:"profile" "{name}"')
    return queries

def gen_domain(params: Dict[str, str]) -> List[str]:
    domain = params.get('domain', '')
    name = params.get('name', '')
    if not domain:
        return []
    queries = []
    if name:
        queries.append(f'site:{domain} "{name}"')
    queries.append(f'site:{domain} filetype:xls')
    if name and ' ' in name:
        parts = name.lower().split()
        if len(parts) >= 2:
            first, last = parts[0], parts[-1]
            possible_emails = [
                f"{first}.{last}@{domain}",
                f"{first}{last}@{domain}",
                f"{first}_{last}@{domain}",
                f"{first[0]}{last}@{domain}"
            ]
            for em in possible_emails:
                queries.append(f'"{em}"')
    if name:
        queries.append(f'"{name}" @{domain}')
    queries.append(f'"@{domain}" filetype:pdf OR filetype:doc')
    return queries

def gen_cross(params: Dict[str, str]) -> List[str]:
    name = params.get('name', '')
    email = params.get('email', '')
    phone = params.get('phone', '')
    city = params.get('city', '')
    company = params.get('company', '')
    queries = []
    if name and email:
        queries.append(f'"{name}" "{email}" site:vk.com')
    if name and phone:
        queries.append(f'"{name}" "{phone}" site:telegram.me')
    if email:
        queries.append(f'"{email}" filetype:xls OR filetype:csv')
    if name:
        queries.append(f'"{name}" filetype:xls OR filetype:csv OR filetype:pdf')
    if name and city and company:
        queries.append(f'intext:"{name}" AND intext:"{city}" AND intext:"работает"')
    elif name and city:
        queries.append(f'intext:"{name}" AND intext:"{city}"')
    elif name and company:
        queries.append(f'intext:"{name}" AND intext:"{company}"')
    return queries

def gen_exclude(params: Dict[str, str]) -> List[str]:
    name = params.get('name', '')
    exclude_site = params.get('exclude_site', '')
    exclude_filetype = params.get('exclude_filetype', '')
    exclude_word = params.get('exclude_word', '')
    if not name:
        return []
    queries = []
    if exclude_site:
        queries.append(f'"{name}" -site:{exclude_site}')
    if exclude_filetype:
        queries.append(f'"{name}" -filetype:{exclude_filetype}')
    if exclude_word:
        queries.append(f'"{name}" -"{exclude_word}"')
    if not (exclude_site or exclude_filetype or exclude_word):
        queries.append(f'"{name}" -site:vk.com')
    return queries

def gen_cache(params: Dict[str, str]) -> List[str]:
    url = params.get('url', '')
    if not url:
        return []
    return [f'cache:{url}']

def gen_blog_forums(params: Dict[str, str]) -> List[str]:
    name = params.get('name', '')
    if not name:
        return []
    sites = ['reddit.com', 'quora.com', 'habr.com', 'stackoverflow.com']
    return [f'site:{site} "{name}"' for site in sites]

def gen_username(params: Dict[str, str]) -> List[str]:
    username = params.get('username', '')
    if not username:
        return []
    sites = ['vk.com', 'instagram.com', 'twitter.com']
    queries = []
    for site in sites:
        queries.append(f'"{username}" site:{site}')
    queries.append(f'inurl:"/{username}"')
    queries.append(f'intext:"{username}"')
    return queries

def gen_hashtags(params: Dict[str, str]) -> List[str]:
    name = params.get('name', '')
    if not name:
        return []
    tag = name.replace(' ', '')
    queries = []
    queries.append(f'#{tag} site:twitter.com')
    queries.append(f'"@{name}" site:twitter.com')
    if ' ' in name:
        parts = name.split()
        if len(parts) >= 2:
            nick = parts[0] + parts[-1]
            queries.append(f'"@{nick}" site:twitter.com')
    return queries

def gen_ip(params: Dict[str, str]) -> List[str]:
    ip = params.get('ip', '')
    if not ip:
        return []
    queries = []
    queries.append(f'"IP {ip}"')
    queries.append(f'intext:"{ip}"')
    queries.append(f'site:abuseipdb.com "{ip}"')
    return queries

def gen_typos(params: Dict[str, str]) -> List[str]:
    name = params.get('name', '')
    if not name:
        return []
    variants = params.get('typos', '')
    if not variants:
        return [f'intext:"{name}"']
    queries = []
    for v in variants.split(','):
        v = v.strip()
        if v:
            queries.append(f'intext:"{v}"')
    return queries

def gen_logical(params: Dict[str, str]) -> List[str]:
    name = params.get('name', '')
    city = params.get('city', '')
    if not name:
        return []
    parts = name.split()
    if len(parts) >= 2:
        name_en = params.get('name_en', '')
        if name_en:
            name_or = f'("{name}" OR "{name_en}")'
        else:
            name_or = f'"{name}"'
    else:
        name_or = f'"{name}"'
    if city:
        city_en = params.get('city_en', '')
        if city_en:
            city_or = f'("{city}" OR "{city_en}")'
        else:
            city_or = f'"{city}"'
        return [f'{name_or} AND {city_or}']
    else:
        return [f'{name_or}']

def gen_numbers(params: Dict[str, str]) -> List[str]:
    number = params.get('number', '')
    if not number:
        return []
    return [f'"{number}"', f'{number}']

def gen_wildcard(params: Dict[str, str]) -> List[str]:
    name = params.get('name', '')
    if not name:
        return []
    parts = name.split()
    if len(parts) >= 3:
        queries = [f'"{parts[0]} * {parts[-1]}"']
    elif len(parts) == 2:
        queries = [f'"{parts[0]} * {parts[1]}"']
    else:
        queries = [f'"{name}*"']
    pattern = params.get('wildcard_pattern', '')
    if pattern:
        queries.append(pattern)
    return queries

# ========================== ОСНОВНОЙ МОДУЛЬ ==========================

CATEGORIES = [
    (1, "Поиск профилей в соцсетях и мессенджерах", gen_profiles,
     {"name": "Имя и фамилия (например, Иван Иванов)"}),
    (2, "Поиск email, почтовых баз и утечек", gen_email,
     {"email": "Email адрес (например, ivan.ivanov@example.com)"}),
    (3, "Поиск телефонных номеров и связанных страниц", gen_phone,
     {"phone": "Номер телефона (например, +79991234567)"}),
    (4, "Поиск документов, резюме, CV", gen_docs,
     {"name": "Имя и фамилия"}),
    (5, "Поиск по фото, изображениям", gen_photos,
     {"name": "Имя и фамилия"}),
    (6, "Поиск форумных аккаунтов и комментариев", gen_forums,
     {"name": "Имя и фамилия"}),
    (7, "Поиск утечек с помощью дорков (файлы, базы, логи)", gen_leaks,
     {"name": "Имя и фамилия (опционально)"}),
    (8, "Поиск по геолокации и связям", gen_geo,
     {"name": "Имя и фамилия", "city": "Город (опционально)", "company": "Компания (опционально)"}),
    (9, "Поиск закрытых страниц, админок, профилей", gen_admin,
     {"name": "Имя и фамилия (опционально)"}),
    (10, "Поиск по доменам и корпоративной почте", gen_domain,
     {"domain": "Домен (например, example.com)", "name": "Имя и фамилия (опционально)"}),
    (11, "Совмещённые запросы (кросс-проверка)", gen_cross,
     {"name": "Имя и фамилия", "email": "Email", "phone": "Телефон", "city": "Город", "company": "Компания"}),
    (12, "Исключение ненужных результатов", gen_exclude,
     {"name": "Имя и фамилия", "exclude_site": "Сайт для исключения", "exclude_filetype": "Тип файла для исключения", "exclude_word": "Слово для исключения"}),
    (13, "Проверка сайтов через кэш Google", gen_cache,
     {"url": "URL страницы (например, vk.com/id123456)"}),
    (14, "Поиск по форумам, блогам и Q&A", gen_blog_forums,
     {"name": "Имя и фамилия"}),
    (15, "Поиск соцсетей по никнейму (username)", gen_username,
     {"username": "Никнейм (например, ivan_ivanov)"}),
    (16, "Поиск по хэштегам и упоминаниям", gen_hashtags,
     {"name": "Имя и фамилия"}),
    (17, "Поиск по IP", gen_ip,
     {"ip": "IP-адрес (например, 192.168.1.1)"}),
    (18, "Поиск по текстам с ошибками/описаниям", gen_typos,
     {"name": "Имя и фамилия", "typos": "Варианты с ошибками через запятую (опционально)"}),
    (19, "Расширенные логические запросы", gen_logical,
     {"name": "Имя и фамилия", "city": "Город", "name_en": "Имя латиницей (опционально)", "city_en": "Город латиницей (опционально)"}),
    (20, "Поиск по числам и коду (ИНН, паспорт)", gen_numbers,
     {"number": "Номер (например, 1234 567890)"}),
    (21, "Использование подстановочных символов (wildcards)", gen_wildcard,
     {"name": "Имя и фамилия", "wildcard_pattern": "Дополнительный шаблон с * (опционально)"}),
]

def show_menu():
    """Выводит меню в две колонки: слева 1–10, справа 11–20, внизу по центру 21."""
    print(colored("\n" + "=" * 80, CYAN))
    print(colored("   ВЫБЕРИТЕ КАТЕГОРИЮ ДЛЯ ГЕНЕРАЦИИ", YELLOW, bold=True))
    print(colored("=" * 80, CYAN))

    left_items = []
    right_items = []
    for i in range(1, 11):
        left_items.append(f"{colored(str(i), GREEN, bold=True):2}. {CATEGORIES[i-1][1]}")
    for i in range(11, 21):
        right_items.append(f"{colored(str(i), GREEN, bold=True):2}. {CATEGORIES[i-1][1]}")

    # Ширина левой колонки — 70 символов, добавим разделитель
    col_width = 70
    for left, right in zip(left_items, right_items):
        # Обрезаем левую строку, если она длиннее col_width, чтобы не сломать верстку
        left_str = left[:col_width-3] + "..." if len(left) > col_width else left
        print(f"{left_str:<{col_width}} │ {right}")

    # 21-й пункт по центру
    item21 = f"{colored('21', GREEN, bold=True)}. {CATEGORIES[20][1]}"
    print(" " * ((350 - len(item21)) // 2) + item21)

    # Пункт выхода отдельно
    print(colored(" 0. Выход", RED, bold=True))
    print(colored("-" * 80, CYAN))

def get_params_for_category(cat_info):
    _, _, _, param_desc = cat_info
    params = {}
    print(colored("\nВведите необходимые данные (пустое поле пропускается, если оно опционально):", YELLOW))
    for key, desc in param_desc.items():
        val = input(f"{colored(desc, CYAN)}: ").strip()
        if val:
            params[key] = val
    return params

def main():
    print_ascii_art()
    while True:
        show_menu()
        try:
            choice = int(input(colored("Выберите номер категории (0 для выхода): ", GREEN, bold=True)))
        except ValueError:
            print(colored("Пожалуйста, введите число.", RED))
            continue

        if choice == 0:
            print(colored("До свидания!", YELLOW, bold=True))
            break

        cat_info = None
        for c in CATEGORIES:
            if c[0] == choice:
                cat_info = c
                break
        if not cat_info:
            print(colored("Неверный номер. Попробуйте снова.", RED))
            continue

        params = get_params_for_category(cat_info)
        if not params:
            print(colored("Вы не ввели ни одного параметра. Запросы не могут быть сгенерированы.", RED))
            continue

        generator = cat_info[2]
        queries = generator(params)
        if not queries:
            print(colored("Не удалось сгенерировать запросы. Возможно, недостаточно данных.", RED))
            continue

        print(colored(f"\nСгенерировано {len(queries)} запросов:", YELLOW, bold=True))
        print_queries(queries)

        while True:
            action = input(colored("Введите номер запроса, чтобы открыть в браузере, 'a' - открыть все, 'n' - продолжить, 'q' - выход: ", CYAN)).strip().lower()
            if action == 'q':
                print(colored("До свидания!", YELLOW, bold=True))
                return
            if action == 'n':
                break
            if action == 'a':
                for q in queries:
                    webbrowser.open(make_google_url(q))
                break
            try:
                idx = int(action)
                if 1 <= idx <= len(queries):
                    webbrowser.open(make_google_url(queries[idx-1]))
                    break
                else:
                    print(colored("Номер вне диапазона.", RED))
            except ValueError:
                print(colored("Некорректный ввод.", RED))

if __name__ == "__main__":
    main()
