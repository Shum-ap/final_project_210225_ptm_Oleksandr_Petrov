import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()


# 📦 Получение подключения к базе данных
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )


# 🔁 Универсальный обработчик SQL-запросов
def run_query(query, params=(), dictionary=False):
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=dictionary)
        cursor.execute(query, params)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# 🔍 Поиск по ключевому слову (в названии и описании фильма)
def search_by_keyword(keyword, offset=0, limit=10):
    query = """
        SELECT
            f.title,
            c.name AS genre,
            f.release_year AS year,
            f.description
        FROM film f
        JOIN film_category fc ON f.film_id = fc.film_id
        JOIN category c ON fc.category_id = c.category_id
        WHERE f.title LIKE %s OR f.description LIKE %s
        ORDER BY f.title
        LIMIT %s OFFSET %s;
    """
    return run_query(query, (f"%{keyword}%", f"%{keyword}%", limit, offset), dictionary=True)


# 🎞 Получение уникальных жанров с диапазонами годов и количеством фильмов
def get_genres_with_years():
    query = """
        SELECT
            c.name AS genre,
            MIN(f.release_year) AS min_year,
            MAX(f.release_year) AS max_year,
            COUNT(*) AS film_count
        FROM film f
        JOIN film_category fc ON f.film_id = fc.film_id
        JOIN category c ON fc.category_id = c.category_id
        GROUP BY c.name
        ORDER BY c.name;
    """
    return run_query(query)


# 🎯 Поиск по жанру и диапазону лет
def search_by_genre_and_year(genre, start_year, end_year, offset=0, limit=10):
    query = """
        SELECT
            f.title,
            c.name AS genre,
            f.release_year AS year,
            f.description
        FROM film f
        JOIN film_category fc ON f.film_id = fc.film_id
        JOIN category c ON fc.category_id = c.category_id
        WHERE c.name = %s AND f.release_year BETWEEN %s AND %s
        ORDER BY f.release_year
        LIMIT %s OFFSET %s;
    """
    return run_query(query, (genre, start_year, end_year, limit, offset), dictionary=True)
