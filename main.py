from mysql_connector import (
    search_by_keyword, get_genres_and_years, search_by_genre_and_year
)
from log_writer import log_search
from log_stats import get_recent_searches, get_top_searches
from formatter import print_results

def paginate_search(search_func, log_info, **kwargs):
    offset = 0
    while True:
        results = search_func(offset=offset, **kwargs)
        print_results(results)
        log_search(**log_info, results_count=len(results))
        if len(results) < 10:
            break
        next_page = input("Показать ещё 10? (y/n): ")
        if next_page.lower() != 'y':
            break
        offset += 10

def main():
    while True:
        print("\nМеню:")
        print("1. Поиск по ключевому слову")
        print("2. Поиск по жанру и году")
        print("3. Топ-5 популярных запросов")
        print("4. Последние 5 запросов")
        print("0. Выход")

        choice = input("Выберите опцию: ")

        if choice == '1':
            keyword = input("Введите ключевое слово: ")
            paginate_search(
                search_by_keyword,
                log_info={"search_type": "keyword", "params": {"keyword": keyword}},
                keyword=keyword
            )

        elif choice == '2':
            genres, min_year, max_year = get_genres_and_years()
            print("\nЖанры:", ", ".join(genres))
            print(f"Годы: от {min_year} до {max_year}")

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

        elif choice == '3':
            print("Топ 5 популярных запросов:")
            for item in get_top_searches():
                print(item)

        elif choice == '4':
            print("Последние 5 запросов:")
            for item in get_recent_searches():
                print(item)

        elif choice == '0':
            print("Выход...")
            break

        else:
            print("Неверный ввод. Попробуйте снова.")

if __name__ == '__main__':
    main()
