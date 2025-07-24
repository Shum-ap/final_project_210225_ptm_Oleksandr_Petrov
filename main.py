from dotenv import load_dotenv
load_dotenv()

from mysql_connector import (
    search_by_keyword,
    get_genres_with_years,
    search_by_genre_and_year
)
from log_writer import log_search
from log_stats import get_recent_searches, get_top_searches
from formatter import print_results
from tabulate import tabulate

# 🔁 Постраничный вывод результатов с переходом по страницам
def paginate_search(search_func, log_info, **kwargs):
    offset = 0
    limit = 10
    current_page = 1

    # Получаем все результаты заранее
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

    while True:
        start_idx = (current_page - 1) * limit
        end_idx = start_idx + limit
        current_batch = all_results[start_idx:end_idx]

        print_results(current_batch, start_index=start_idx + 1)
        log_search(**log_info, results_count=len(current_batch))

        print(f"📄 Страница {current_page} из {total_pages} | Показано {min(end_idx, total_results)} из {total_results}")

        user_input = input(
            "➡️ Введите 'n' — следующая, 'p' — предыдущая, 'q' — выход, номер страницы: ").strip().lower()

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
1

# 🧠 Главное меню
def main():
    while True:
        print("\nМеню:")
        print("1. Поиск по ключевому слову")
        print("2. Поиск по жанру и году")
        print("3. История запросов (топ или последние)")
        print("0. Выход")

        choice = input("Выберите опцию: ").strip()

        # 🔍 Поиск по ключевому слову
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

        # 🎞 Поиск по жанру и году
        elif choice == '2':
            genre_data = get_genres_with_years()  # [(genre, min_year, max_year, count), ...]

            table = []
            for i, (genre, g_min, g_max, count) in enumerate(genre_data):
                table.append([i + 1, genre, g_min, g_max, count])

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

            try:
                year_from = int(input("Год с: ").strip())
                year_to = int(input("Год до: ").strip())
            except ValueError:
                print("❌ Ошибка: введите корректные целые числа.")
                continue

            if year_from < genre_min or year_to > genre_max or year_from > year_to:
                print(f"❌ Годы должны быть в пределах {genre_min}–{genre_max}, и 'с' ≤ 'до'.")
                continue

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

        # 🧾 История запросов: топ или последние
        elif choice == '3':
            print("\n📚 История запросов:")
            print("1. Топ-5 популярных запросов")
            print("2. Последние 5 уникальных запросов")
            sub_choice = input("Выберите тип (1 или 2): ").strip()

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
                        headers=["Тип запроса", "Жанр / Ключевое", "Годы", "Кол-во", "Время"],
                        tablefmt="grid"
                    ))
            else:
                print("❌ Неверный выбор. Возврат в меню.")

        elif choice == '0':
            print("👋 Выход...")
            break
        else:
            print("❌ Неверный ввод. Попробуйте снова.")


# ▶️ Запуск
if __name__ == '__main__':
    main()
