import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()


# 🔍 Поиск по ключевому слову (в названии и описании фильма)
def search_by_keyword(keyword, offset=0, limit=10):
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

    cursor = connection.cursor(dictionary=True)
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
    cursor.execute(query, (f"%{keyword}%", f"%{keyword}%", limit, offset))
    results = cursor.fetchall()

    cursor.close()
    connection.close()
    return results


# 🎞 Получение уникальных жанров с диапазонами годов и количеством фильмов
def get_genres_with_years():
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

    cursor = connection.cursor()
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
    cursor.execute(query)
    results = cursor.fetchall()

    cursor.close()
    connection.close()
    return results  # [(genre, min_year, max_year, count), ...]


# 🎯 Поиск по жанру и диапазону лет
def search_by_genre_and_year(genre, start_year, end_year, offset=0, limit=10):
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

    cursor = connection.cursor(dictionary=True)
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
    cursor.execute(query, (genre, start_year, end_year, limit, offset))
    results = cursor.fetchall()

    cursor.close()
    connection.close()
    return results
