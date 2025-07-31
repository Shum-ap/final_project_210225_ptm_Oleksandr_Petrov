"""
🎬 final_project_210225_ptm_Oleksandr_Petrov
Консольное приложение для поиска фильмов с поддержкой языка, пагинацией и дружелюбным UX.
"""

from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Импорт модулей
from mysql_connector import (
    search_by_keyword,
    get_genres_with_years,
    search_by_genre_and_year
)
from log_writer import log_search
from log_stats import get_recent_searches, get_top_searches
from formatter import format_table


# 🌍 Языковые строки
LANGUAGES = {
    'ru': {
        'main_menu': '📘 Главное меню:',
        'search_keyword': '1. 🔍 Поиск по ключевому слову',
        'search_genre_year': '2. 🎞️ Поиск по жанру и диапазону годов',
        'history': '3. 📚 История запросов',
        'language': '4. 🔤 Сменить язык',
        'exit': '0. 🛑 Выход',
        'choose': 'Выберите опцию: ',
        'lang_changed_en': '✅ Язык изменён на английский.',
        'lang_changed_ru': '✅ Язык изменён на русский.',
        'enter_keyword': '🔑 Введите ключевое слово: ',
        'no_keyword': '❌ Ключевое слово не может быть пустым.',
        'genre_title': '🎬 Доступные жанры:',
        'enter_genre': 'Введите номер или название жанра: ',
        'invalid_genre': '❌ Жанр не найден.',
        'year_range': '📅 Диапазон годов для жанра {}: {}–{}',
        'enter_year_from': 'Год от',
        'enter_year_to': 'Год до',
        'invalid_year': '❌ Годы должны быть в пределах {}–{}, и "от" ≤ "до".',
        'no_results': '⚠️ Ничего не найдено.',
        'exit_msg': '👋 Выход...',
        'keyboard_interrupt': '👋 Программа завершена пользователем.',
        'unexpected_error': '⚠️ Неожиданная ошибка: {}',
        'retry_prompt': '🔁 Введите "r" чтобы повторить, "m" для возврата в меню: ',
        'invalid_input': '❌ Неверный ввод.',
    },
    'en': {
        'main_menu': '📘 Main Menu:',
        'search_keyword': '1. 🔍 Search by keyword',
        'search_genre_year': '2. 🎞️ Search by genre and year range',
        'history': '3. 📚 Search history',
        'language': '4. 🔤 Change language',
        'exit': '0. 🛑 Exit',
        'choose': 'Choose an option: ',
        'lang_changed_en': '✅ Language changed to English.',
        'lang_changed_ru': '✅ Language changed to Russian.',
        'enter_keyword': '🔑 Enter keyword: ',
        'no_keyword': '❌ Keyword cannot be empty.',
        'genre_title': '🎬 Available genres:',
        'enter_genre': 'Enter genre number or name: ',
        'invalid_genre': '❌ Genre not found.',
        'year_range': '📅 Year range for {}: {}–{}',
        'enter_year_from': 'Year from',
        'enter_year_to': 'Year to',
        'invalid_year': '❌ Years must be within {}–{} and "from" ≤ "to".',
        'no_results': '⚠️ No results found.',
        'exit_msg': '👋 Exiting...',
        'keyboard_interrupt': '👋 Program interrupted by user.',
        'unexpected_error': '⚠️ Unexpected error: {}',
        'retry_prompt': '🔁 Type "r" to retry, "m" to return to menu: ',
        'invalid_input': '❌ Invalid input.',
    }
}

# Глобальная переменная языка
CURRENT_LANGUAGE = 'ru'


def tr(key):
    """Возвращает строку на текущем языке"""
    return LANGUAGES[CURRENT_LANGUAGE].get(key, key)


# 🗂️ Пагинация результатов
def paginate_search(search_func, log_info, **kwargs):
    limit = 10
    all_results = []
    offset = 0

    while True:
        batch = search_func(offset=offset, limit=limit, **kwargs)
        if not batch:
            break
        all_results.extend(batch)
        if len(batch) < limit:
            break
        offset += limit

    total = len(all_results)
    if total == 0:
        print(tr('no_results'))
        return

    # Логируем один раз
    log_search(**log_info, results_count=total)

    total_pages = (total + limit - 1) // limit
    current_page = 1

    while True:
        start_idx = (current_page - 1) * limit
        page_results = all_results[start_idx:start_idx + limit]

        # Вывод таблицы
        print(format_table(page_results, page=current_page, total=total, limit=limit))

        # Улучшенное сообщение навигации
        base_msg = "➡️"
        if current_page < total_pages:
            base_msg += " 'n' — следующая"
        if current_page > 1:
            base_msg += ", 'p' — предыдущая"
        base_msg += ", 'q' — выход, или номер страницы: "

        try:
            user_input = input(base_msg).strip().lower()
        except KeyboardInterrupt:
            print(f"\n\n👋 {tr('keyboard_interrupt')}")
            break

        if user_input == 'q':
            print(f"\n🚪 {tr('exit_msg')}\n")
            break
        elif user_input == 'n' and current_page < total_pages:
            current_page += 1
        elif user_input == 'p' and current_page > 1:
            current_page -= 1
        elif user_input.isdigit():
            page = int(user_input)
            if 1 <= page <= total_pages:
                current_page = page
            else:
                print("❌ " + tr('invalid_input'))
        else:
            print("❌ " + tr('invalid_input'))


# 📚 Подменю истории: остаётся в меню до явного выхода
def history_submenu():
    """Подменю истории: пользователь может просматривать, пока не нажмёт 0."""
    while True:
        print(f"\n📚 {tr('history')}:")
        print("1. 📊 Топ-5 популярных запросов")
        print("2. 🕒 Последние 5 уникальных запросов")
        print("0. ◀️ Выйти в основное меню")

        sub_choice = input(tr('choose')).strip()

        if sub_choice == '1':
            top = get_top_searches(limit=5)
            if not top:
                print("⚠️ Нет данных.")
            else:
                from tabulate import tabulate
                table = []
                for entry in top:
                    params = entry["_id"]
                    count = entry["count"]
                    if "keyword" in params:
                        query_type = "По ключевому слову" if CURRENT_LANGUAGE == 'ru' else "By keyword"
                        query_str = params["keyword"]
                    elif "genre" in params:
                        query_type = "По жанру и году" if CURRENT_LANGUAGE == 'ru' else "By genre and year"
                        query_str = f"{params['genre']} ({params['from']}–{params['to']})"
                    else:
                        query_type = "Неизвестный" if CURRENT_LANGUAGE == 'ru' else "Unknown"
                        query_str = str(params)
                    table.append([query_type, query_str, count])
                headers = ["Тип", "Параметры", "Кол-во"] if CURRENT_LANGUAGE == 'ru' else ["Type", "Params", "Count"]
                print(tabulate(table, headers=headers, tablefmt="grid"))

        elif sub_choice == '2':
            recent = get_recent_searches(limit=5)
            if not recent:
                print("⚠️ Нет данных.")
            else:
                from tabulate import tabulate
                table = []
                for entry in recent:
                    search_type = entry.get("search_type", "-")
                    params = entry.get("params", {})
                    count = entry.get("results_count", 0)
                    timestamp = entry.get("timestamp", "-")[:19]
                    genre_or_kw = params.get("keyword") or params.get("genre", "-")
                    year_range = f"{params.get('from', '?')}–{params.get('to', '?')}" if 'from' in params else "-"
                    table.append([search_type, genre_or_kw, year_range, count, timestamp])
                headers = ["Тип", "Ключ", "Годы", "Найдено", "Время"] if CURRENT_LANGUAGE == 'ru' else ["Type", "Query", "Years", "Found", "Time"]
                print(tabulate(table, headers=headers, tablefmt="grid"))

        elif sub_choice == '0':
            print("🚪 Возврат в главное меню...\n")
            break  # Только здесь выходим

        else:
            print("❌ " + tr('invalid_input'))


# 🧠 Главное меню
def main():
    global CURRENT_LANGUAGE

    # ✅ Приветствие при запуске
    welcome = "📘 Добро пожаловать в MovieSearch CLI!" if CURRENT_LANGUAGE == 'ru' else "📘 Welcome to MovieSearch CLI!"
    print(welcome)
    print("-" * 50)  # Визуальный разделитель

    while True:
        try:
            print(f"\n{tr('main_menu')}")
            print(tr('search_keyword'))
            print(tr('search_genre_year'))
            print(tr('history'))
            print(tr('language'))
            print(tr('exit'))
            choice = input(tr('choose')).strip()

            # 🔍 Все if/elif должны быть ВНУТРИ try
            if choice == '1':
                keyword = None
                while True:
                    keyword_input = input(tr('enter_keyword')).strip()
                    if keyword_input:
                        keyword = keyword_input
                        break
                    print(tr('no_keyword'))
                    action = input(tr('retry_prompt')).strip().lower()
                    if action in ('m', 'меню', 'menu'):
                        keyword = None
                        break
                if keyword is None:
                    continue
                paginate_search(
                    search_by_keyword,
                    log_info={"search_type": "keyword", "params": {"keyword": keyword}},
                    keyword=keyword
                )

            elif choice == '2':
                genres = get_genres_with_years()
                if not genres:
                    msg = "⚠️ Нет данных по жанрам." if CURRENT_LANGUAGE == 'ru' else "⚠️ No genre data."
                    print(msg)
                    continue

                from tabulate import tabulate
                table_data = [[i, g, y_min, y_max, cnt] for i, (g, y_min, y_max, cnt) in enumerate(genres, 1)]
                headers = ["№", "Жанр", "С", "По", "Фильмов"] if CURRENT_LANGUAGE == 'ru' else ["#", "Genre", "From", "To", "Count"]
                print(f"\n{tr('genre_title')}")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))

                # Ввод жанра
                genre = None
                min_year, max_year = None, None
                while True:
                    genre_input = input(tr('enter_genre')).strip()
                    if not genre_input:
                        print(tr('invalid_genre'))
                    else:
                        if genre_input.isdigit():
                            idx = int(genre_input) - 1
                            if 0 <= idx < len(genres):
                                genre, min_year, max_year, _ = genres[idx]
                                break
                        else:
                            matched = [g for g in genres if g[0].lower() == genre_input.lower()]
                            if matched:
                                genre, min_year, max_year, _ = matched[0]
                                break
                        print(tr('invalid_genre'))

                    action = input(tr('retry_prompt')).strip().lower()
                    if action in ('m', 'меню', 'menu'):
                        genre = None
                        break

                if genre is None:
                    continue

                print(tr('year_range').format(genre, min_year, max_year))

                # Ввод годов
                from_year, to_year = None, None
                while True:
                    try:
                        from_year_input = input(f"{tr('enter_year_from')} ({min_year}): ").strip()
                        to_year_input = input(f"{tr('enter_year_to')} ({max_year}): ").strip()

                        from_year = int(from_year_input) if from_year_input else min_year
                        to_year = int(to_year_input) if to_year_input else max_year

                        if from_year > to_year:
                            print(tr('invalid_year').replace("и \"от\" ≤ \"до\"", "and 'from' ≤ 'to'"))
                        elif from_year < min_year or to_year > max_year:
                            print(tr('invalid_year').format(min_year, max_year))
                        else:
                            break
                    except ValueError:
                        print("❌ Ошибка: введите число.")

                    action = input(tr('retry_prompt')).strip().lower()
                    if action in ('m', 'меню', 'menu'):
                        from_year, to_year = None, None
                        break

                if from_year is None:
                    continue

                paginate_search(
                    search_by_genre_and_year,
                    log_info={
                        "search_type": "genre_year",
                        "params": {"genre": genre, "from": from_year, "to": to_year}
                    },
                    genre=genre,
                    start_year=from_year,
                    end_year=to_year
                )

            elif choice == '3':
                history_submenu()

            elif choice == '4':
                if CURRENT_LANGUAGE == 'ru':
                    CURRENT_LANGUAGE = 'en'
                    print(tr('lang_changed_en'))
                else:
                    CURRENT_LANGUAGE = 'ru'
                    print(tr('lang_changed_ru'))

            elif choice == '0':
                goodbye = "👋 Спасибо за использование! До свидания." if CURRENT_LANGUAGE == 'ru' else "👋 Thank you for using MovieSearch CLI! Goodbye."
                print(f"\n{goodbye}")
                break

            else:
                print("❌ " + tr('invalid_input'))

        except KeyboardInterrupt:
            goodbye = "👋 Программа завершена пользователем." if CURRENT_LANGUAGE == 'ru' else "👋 Program interrupted by user."
            print(f"\n\n{goodbye}")
            break
        except Exception as e:
            print(tr('unexpected_error').format(e))


# ▶️ Запуск приложения
if __name__ == "__main__":
    main()