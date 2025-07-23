# Импорт логики поиска, логирования и вывода
from mysql_connector import (
    search_by_keyword,
    get_genres_and_years,
    search_by_genre_and_year
)
from log_writer import log_search                      # запись логов в MongoDB
from log_stats import get_recent_searches, get_top_searches  # получение статистики
from formatter import print_results                   # форматированный вывод фильмов
from tabulate import tabulate                         # вывод таблиц в консоли


# Общая функция постраничного поиска (по 10 результатов за раз)
def paginate_search(search_func, log_info, **kwargs):
    offset = 0
    while True:
        results = search_func(offset=offset, **kwargs)         # получение результатов
        print_results(results)                                 # вывод фильмов
        log_search(**log_info, results_count=len(results))     # логируем запрос
        if len(results) < 10:                                  # если конец — выходим
            break
        next_page = input("Показать ещё 10? (y/n): ")
        if next_page.lower() != 'y':
            break
        offset += 10


# Главное меню
def main():
    while True:
        print("\nМеню:")
        print("1. Поиск по ключевому слову")
        print("2. Поиск по жанру и году")
        print("3. Топ-5 популярных запросов")
        print("4. Последние 5 запросов")
        print("0. Выход")

        choice = input("Выберите опцию: ")

        # Поиск по названию фильма
        if choice == '1':
            keyword = input("Введите ключевое слово: ")
            paginate_search(
                search_by_keyword,
                log_info={"search_type": "keyword", "params": {"keyword": keyword}},
                keyword=keyword
            )

        # Поиск по жанру и годовому диапазону
        elif choice == '2':
            genres, min_year, max_year = get_genres_and_years()
            print("\nДоступные жанры:")
            print(", ".join(genres))
            print(f"Диапазон годов: {min_year} – {max_year}")

            genre = input("Введите жанр: ")
            year_from = int(input("Год с: "))
            year_to = int(input("Год до: "))

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

        # Топ-5 самых частых запросов (по группировке в MongoDB)
        elif choice == '3':
            print("\n📊 Топ 5 популярных запросов:\n")
            top = get_top_searches()

            if not top:
                print("⚠️ Нет данных.")
            else:
                table = []
                for entry in top:
                    params = entry["_id"]
                    count = entry["count"]

                    # Определяем тип запроса по параметрам
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

        # Последние 5 запросов (по дате)
        elif choice == '4':
            print("\n🕒 Последние 5 запросов:\n")
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

                    # Формируем строку параметров в зависимости от типа
                    if search_type == "keyword":
                        param_str = f"'{params.get('keyword', '')}'"
                    elif search_type == "genre_year":
                        param_str = f"{params.get('genre')} ({params.get('from')}–{params.get('to')})"
                    else:
                        param_str = str(params)

                    table.append([search_type, param_str, count, timestamp])

                print(tabulate(
                    table,
                    headers=["Тип", "Параметры", "Кол-во результатов", "Время"],
                    tablefmt="grid"
                ))

        # Завершение программы
        elif choice == '0':
            print("👋 Выход...")
            break

        else:
            print("❌ Неверный ввод. Попробуйте снова.")


# Запуск программы
if __name__ == '__main__':
    main()
