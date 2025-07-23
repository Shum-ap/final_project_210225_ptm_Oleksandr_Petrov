import pymysql
from config import MYSQL_CONFIG

# 📦 Устанавливает соединение с базой данных MySQL (Sakila)
def get_connection():
    return pymysql.connect(**MYSQL_CONFIG)


# 🔍 Поиск фильмов по ключевому слову (в названии)
def search_by_keyword(keyword, offset=0, limit=10):
    query = """
    SELECT title, release_year, description
    FROM film
    WHERE title LIKE %s
    LIMIT %s OFFSET %s;
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (f'%{keyword}%', limit, offset))
            return cursor.fetchall()
    finally:
        conn.close()


# 📋 Получение списка жанров и диапазона годов выпуска всех фильмов
def get_genres_and_years():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Запрос жанров
            cursor.execute("SELECT name FROM category;")
            genres = [row[0] for row in cursor.fetchall()]

            # Запрос минимального и максимального года
            cursor.execute("SELECT MIN(release_year), MAX(release_year) FROM film;")
            min_year, max_year = cursor.fetchone()

            return genres, min_year, max_year
    finally:
        conn.close()


# 🔍 Поиск фильмов по жанру и диапазону годов выпуска
def search_by_genre_and_year(genre, start_year, end_year, offset=0, limit=10):
    query = """
    SELECT f.title, f.release_year, f.description
    FROM film f
    JOIN film_category fc ON f.film_id = fc.film_id
    JOIN category c ON c.category_id = fc.category_id
    WHERE c.name = %s AND f.release_year BETWEEN %s AND %s
    LIMIT %s OFFSET %s;
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (genre, start_year, end_year, limit, offset))
            return cursor.fetchall()
    finally:
        conn.close()
