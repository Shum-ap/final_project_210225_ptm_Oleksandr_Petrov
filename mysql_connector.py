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


# 📋 Возвращает жанры, диапазоны годов и количество фильмов в каждом жанре
def get_genres_with_years():
    query = """
    SELECT c.name, MIN(f.release_year) AS min_year, MAX(f.release_year) AS max_year, COUNT(*) AS film_count
    FROM category c
    JOIN film_category fc ON c.category_id = fc.category_id
    JOIN film f ON f.film_id = fc.film_id
    GROUP BY c.name
    ORDER BY c.name;
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
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
