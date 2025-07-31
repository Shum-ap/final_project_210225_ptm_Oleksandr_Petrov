from dotenv import load_dotenv
load_dotenv()

from mysql_connector import (
    search_by_keyword,
    get_genres_with_years,
    search_by_genre_and_year
)
from log_writer import log_search
from log_stats import get_recent_searches, get_top_searches
from tabulate import tabulate


# 🗂️ Пагинация результатов с переходами по страницам
def paginate_search(search_func, log_info, **kwargs):
    offset = 0
    limit = 10
    current_page = 1

    all_results = []
    while True:
        batch = search_func(offset=len(all_results), **kwargs)
        if not batch:
            break
        all_results.extend(batch)
        if len(batch) < limit:
            break

    total_results = len(all_results)
    total_pages = (total_results + limit - 1) // limit

    if total_results == 0:
        print("⚠️ Ничего не найдено.")
        return

    # ✅ Логировать один раз
    log_search(**log_info, results_count=total_results)

    while True:
        start_idx = (current_page - 1) * limit
        end_idx = start_idx + limit
        current_batch = all_results[start_idx:end_idx]

        table = []
        for i, item in enumerate(current_batch, start=start_idx + 1):
            if isinstance(item, (list, tuple)) and len(item) >= 3:
                title, year, desc = item[0], item[1], item[2]
                desc = (desc[:100] + "...") if desc and len(desc) > 100 else desc
                table.append([i, title, year, desc])
            else:
                table.append([i, str(item)])

        headers = ["№", "Название", "Год", "Описание"] if all(len(row) == 4 for row in table) else ["№", "Результат"]
        print(tabulate(table, headers=headers, tablefmt="grid"))

        print(f"📄 Страница {current_page} из {total_pages} | Показано {min(end_idx, total_results)} из {total_results}")

        try:
            user_input = input(
                "➡️ Введите 'n' — следующая, "
                + ("'p' — предыдущая, " if current_page > 1 else "")
                + "'q' — выход, номер страницы: "
            ).strip().lower()
        except KeyboardInterrupt:
            print("\n🚪 Пользователь прервал просмотр. Выход...\n")
            break

        if user_input == 'q':
            print("🚪 Выход из просмотра.\n")
            break
        elif user_input == 'n':
            if current_page < total_pages:
                current_page += 1
            else:
                print("📌 Вы уже на последней странице.")
        elif user_input == 'p':
            if current_page > 1:
                current_page -= 1
            else:
                print("📌 Вы уже на первой странице.")
        elif user_input.isdigit():
            page = int(user_input)
            if 1 <= page <= total_pages:
                current_page = page
            else:
                print("❌ Неверный номер страницы.")
        else:
            print("❌ Команда не распознана.")


# 📚 Меню истории: топ или последние
def history_submenu():
    while True:
        print("\n📚 История запросов:")
        print("1. Топ-5 популярных запросов")
        print("2. Последние 5 уникальных запросов")
        print("0. Выйти в основное меню")
        sub_choice = input("Выберите тип (1, 2 или 0): ").strip()

        if sub_choice == '1':
            print("\n📊 Топ 5 популярных запросов:\n")
            top = get_top_searches()
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
                        query_type = "Неизвестный тип"
                        query_str = str(params)

                    table.append([query_type, query_str, count])

                print(tabulate(table, headers=["Тип запроса", "Параметры", "Количество"], tablefmt="grid"))

        elif sub_choice == '2':
            print("\n🕒 Последние 5 уникальных запросов:\n")
            recent = get_recent_searches()
            if not recent:
                print("⚠️ Нет данных.")
            else:
                table = []
                for entry in recent:
                    search_type = entry.get("search_type", "неизв.")
                    params = entry.get("params", {})
                    count = entry.get("results_count", 0)
                    timestamp = entry.get("timestamp", "-")

                    genre_or_keyword = "-"
                    year_range = "-"
                    if search_type == "keyword":
                        genre_or_keyword = params.get("keyword", "-")
                    elif search_type == "genre_year":
                        genre_or_keyword = params.get("genre", "-")
                        year_range = f"{params.get('from')}–{params.get('to')}"

                    table.append([search_type, genre_or_keyword, year_range, count, timestamp])

                print(tabulate(
                    table,
                    headers=["Тип", "Жанр / Ключевое", "Годы", "Кол-во", "Время"],
                    tablefmt="grid"
                ))
        elif sub_choice == '0':
            print("🚪 Возврат в основное меню...\n")
            break
        else:
            print("❌ Неверный выбор. Попробуйте снова.")


# 🧠 Главное меню приложения
def main():
    while True:
        try:
            print("\n📘 Главное меню:")
            print("1. 🔍 Поиск по ключевому слову")
            print("2. 🎞️ Поиск по жанру и диапазону годов")
            print("3. 📚 История запросов")
            print("0. 🛑 Выход")
            choice = input("Выберите опцию: ").strip()
        except KeyboardInterrupt:
            print("\n👋 Программа завершена пользователем.")
            break

        if choice == '1':
            keyword = input("Введите ключевое слово: ").strip()
            if not keyword:
                print("❌ Ключевое слово не может быть пустым.")
                continue

            paginate_search(
                search_by_keyword,
                log_info={"search_type": "keyword", "params": {"keyword": keyword}},
                keyword=keyword
            )

        elif choice == '2':
            genre_data = get_genres_with_years()
            if not genre_data:
                print("⚠️ Нет данных по жанрам.")
                continue

            table = []
            for idx, (genre, year_min, year_max, count) in enumerate(genre_data, start=1):
                table.append([idx, genre, year_min, year_max, count])

            print("\n🎬 Доступные жанры:\n")
            print(tabulate(
                table,
                headers=["№", "Жанр", "Год от", "Год до", "Фильмов"],
                tablefmt="grid"
            ))

            genre_input = input("\nВведите номер жанра или его название: ").strip()
            genre = None
            genre_min, genre_max = None, None

            if genre_input.isdigit():
                index = int(genre_input) - 1
                if 0 <= index < len(genre_data):
                    genre, genre_min, genre_max, _ = genre_data[index]
                else:
                    print("❌ Неверный номер.")
                    continue
            else:
                found = next(
                    ((g, g_min, g_max, _) for g, g_min, g_max, _ in genre_data if g.lower() == genre_input.lower()),
                    None
                )
                if found:
                    genre, genre_min, genre_max, _ = found
                else:
                    print("❌ Жанр не найден.")
                    continue

            print(f"📅 Диапазон годов для жанра {genre}: {genre_min}–{genre_max}")

            while True:
                try:
                    year_from = int(input("Год с: ").strip())
                    year_to = int(input("Год до: ").strip())
                except ValueError:
                    print("❌ Ошибка: введите корректные целые числа.")
                    continue

                if year_from < genre_min or year_to > genre_max or year_from > year_to:
                    print(f"❌ Годы должны быть в пределах {genre_min}–{genre_max}, и 'с' ≤ 'до'. Попробуйте снова.")
                    continue
                else:
                    break

            paginate_search(
                search_by_genre_and_year,
                log_info={
                    "search_type": "genre_year",
                    "params": {"genre": genre, "from": year_from, "to": year_to}
                },
                genre=genre,
                start_year=year_from,
                end_year=year_to
            )

        elif choice == '3':
            history_submenu()

        elif choice == '0':
            print("👋 Выход...")
            break
        else:
            print("❌ Неверный ввод. Попробуйте снова.")


# ▶️ Запуск
if __name__ == '__main__':
    main()
