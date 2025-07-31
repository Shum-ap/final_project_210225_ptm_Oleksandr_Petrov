"""
🎬 final_project_210225_ptm_Oleksandr_Petrov
Консольное приложение для поиска фильмов с историей запросов.

Модули:
- mysql_connector: поиск в MySQL
- log_writer: логирование в MongoDB
- log_stats: получение статистики
- formatter: табличный вывод (tabulate)
- config + .env: настройки подключения
"""

from dotenv import load_dotenv

# Загрузка переменных окружения из .env
load_dotenv()

# 🔧 Импорт модулей проекта
from mysql_connector import (
    search_by_keyword,
    get_genres_with_years,
    search_by_genre_and_year
)
from log_writer import log_search
from log_stats import get_recent_searches, get_top_searches
from formatter import format_table  # ✅ абстрагируем вывод
from tabulate import tabulate


# 🗂️ Пагинация результатов поиска
def paginate_search(search_func, log_info, **kwargs):
    """
    Постраничный вывод результатов поиска.
    Логирует запрос один раз, после получения всех данных.
    Поддерживает навигацию: следующая, предыдущая, переход по номеру.
    """
    limit = 10
    all_results = []

    # 🔍 Собираем все результаты
    offset = 0
    while True:
        batch = search_func(offset=offset, limit=limit, **kwargs)
        if not batch:
            break
        all_results.extend(batch)
        offset += limit
        if len(batch) < limit:  # меньше, чем лимит → конец
            break

    total = len(all_results)
    if total == 0:
        print("⚠️ Ничего не найдено.")
        return

    # ✅ Логируем только один раз, после полного поиска
    log_search(**log_info, results_count=total)

    # 📄 Пагинация
    total_pages = (total + limit - 1) // limit
    current_page = 1

    while True:
        start_idx = (current_page - 1) * limit
        end_idx = start_idx + limit
        page_results = all_results[start_idx:end_idx]

        # ✅ Используем единый форматировщик
        print(format_table(page_results, page=current_page, total=total, limit=limit))

        try:
            prompt = (
                "➡️ Введите 'n' — следующая, "
                + ("'p' — предыдущая, " if current_page > 1 else "")
                + "'q' — выход, или номер страницы: "
            )
            user_input = input(prompt).strip().lower()
        except KeyboardInterrupt:
            print("\n🚪 Просмотр прерван. Возврат в меню...")
            break

        if user_input == 'q':
            print("🚪 Выход из просмотра.\n")
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
                print("❌ Неверный номер страницы.")
        else:
            print("❌ Неизвестная команда.")


# 📚 Подменю: история запросов
def history_submenu():
    """Показывает топ или последние запросы из MongoDB."""
    while True:
        print("\n📚 История запросов:")
        print("1. 📊 Топ-5 популярных запросов")
        print("2. 🕒 Последние 5 уникальных запросов")
        print("0. ◀️ Выйти в основное меню")

        choice = input("Выберите: ").strip()

        if choice == '1':
            top = get_top_searches(limit=5)
            if not top:
                print("⚠️ Нет данных.")
            else:
                table = []
                for entry in top:
                    params = entry["_id"]
                    count = entry["count"]

                    if "keyword" in params:
                        query_type = "По ключевому слову"
                        query_str = params["keyword"]
                    elif "genre" in params:
                        query_type = "По жанру и году"
                        query_str = f"{params['genre']} ({params['from']}–{params['to']})"
                    else:
                        query_type = "Неизвестный"
                        query_str = str(params)

                    table.append([query_type, query_str, count])

                print(tabulate(table,
                               headers=["Тип", "Параметры", "Кол-во"],
                               tablefmt="grid"))

        elif choice == '2':
            recent = get_recent_searches(limit=5)
            if not recent:
                print("⚠️ Нет данных.")
            else:
                table = []
                for entry in recent:
                    search_type = entry.get("search_type", "неизв.")
                    params = entry.get("params", {})
                    count = entry.get("results_count", 0)
                    timestamp = entry.get("timestamp", "-")

                    genre_or_kw = "-"
                    year_range = "-"
                    if search_type == "keyword":
                        genre_or_kw = params.get("keyword", "-")
                    elif search_type == "genre_year":
                        genre_or_kw = params.get("genre", "-")
                        year_range = f"{params.get('from', '?')}–{params.get('to', '?')}"

                    table.append([search_type, genre_or_kw, year_range, count, timestamp[:19]])

                print(tabulate(table,
                               headers=["Тип", "Ключ", "Годы", "Найдено", "Время"],
                               tablefmt="grid"))

        elif choice == '0':
            print("🚪 Возврат в главное меню...\n")
            break
        else:
            print("❌ Неверный выбор. Попробуйте снова.")


# 🧠 Главное меню
def main():
    """Главная точка входа. Цикл меню с обработкой ввода и ошибок."""
    print("📘 Добро пожаловать в MovieSearch CLI!")

    while True:
        try:
            print("\n📋 Главное меню:")
            print("1. 🔍 Поиск по ключевому слову")
            print("2. 🎞️ Поиск по жанру и диапазону годов")
            print("3. 📚 Просмотр истории запросов")
            print("0. 🛑 Выход")

            choice = input("Выберите опцию: ").strip()

            if choice == '1':
                keyword = input("🔑 Введите ключевое слово: ").strip()
                if not keyword:
                    print("❌ Ключевое слово не может быть пустым.")
                    continue

                paginate_search(
                    search_by_keyword,
                    log_info={"search_type": "keyword", "params": {"keyword": keyword}},
                    keyword=keyword
                )

            elif choice == '2':
                # 🎬 Загружаем доступные жанры
                genres = get_genres_with_years()
                if not genres:
                    print("⚠️ Нет доступных жанров.")
                    continue

                # 🖨️ Показываем таблицу жанров
                table = [[i, g, y_min, y_max, cnt] for i, (g, y_min, y_max, cnt) in enumerate(genres, 1)]
                print("\n🎬 Доступные жанры:")
                print(tabulate(table,
                               headers=["№", "Жанр", "С", "По", "Фильмов"],
                               tablefmt="grid"))

                # 🧩 Обработка выбора жанра
                genre_input = input("Введите номер или название жанра: ").strip()
                selected_genre = None

                if genre_input.isdigit():
                    idx = int(genre_input) - 1
                    if 0 <= idx < len(genres):
                        selected_genre = genres[idx]
                    else:
                        print("❌ Неверный номер.")
                        continue
                else:
                    matched = [g for g in genres if g[0].lower() == genre_input.lower()]
                    if matched:
                        selected_genre = matched[0]
                    else:
                        print("❌ Жанр не найден.")
                        continue

                genre, min_year, max_year, _ = selected_genre
                print(f"📅 Диапазон для '{genre}': {min_year}–{max_year}")

                # 📆 Ввод диапазона лет
                while True:
                    try:
                        from_year = int(input(f"Год от ({min_year}): ") or min_year)
                        to_year = int(input(f"Год до ({max_year}): ") or max_year)
                    except ValueError:
                        print("❌ Введите целое число.")
                        continue

                    if from_year > to_year:
                        print("❌ 'От' не может быть больше 'До'.")
                    elif from_year < min_year or to_year > max_year:
                        print(f"❌ Годы вне диапазона: {min_year}–{max_year}.")
                    else:
                        break

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

            elif choice == '0':
                print("👋 Спасибо за использование! До свидания.")
                break

            else:
                print("❌ Неверная опция. Попробуйте снова.")

        except KeyboardInterrupt:
            print("\n\n👋 Программа завершена по Ctrl+C.")
            break
        except Exception as e:
            print(f"⚠️ Неожиданная ошибка: {e}")


# ▶️ Запуск приложения
if __name__ == "__main__":
    main()