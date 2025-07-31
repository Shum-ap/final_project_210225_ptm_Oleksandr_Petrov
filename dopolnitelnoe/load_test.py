import time
import threading
from mysql_connector import search_by_keyword, search_by_genre_and_year

NUM_THREADS = 100# Кол-во параллельных запросов
KEYWORD = "action"  # Ключевое слово для теста
GENRE = "Action"
YEAR_FROM = 2000
YEAR_TO = 2006

# Статистика
success = 0
fail = 0
lock = threading.Lock()

def test_keyword_search():
    global success, fail
    try:
        results = search_by_keyword(KEYWORD, offset=0, limit=10)
        with lock:
            if results:
                success += 1
            else:
                fail += 1
    except Exception as e:
        with lock:
            fail += 1
        print(f"[ERROR] keyword search: {e}")

def test_genre_year_search():
    global success, fail
    try:
        results = search_by_genre_and_year(GENRE, YEAR_FROM, YEAR_TO, offset=0, limit=10)
        with lock:
            if results:
                success += 1
            else:
                fail += 1
    except Exception as e:
        with lock:
            fail += 1
        print(f"[ERROR] genre-year search: {e}")

def run_load_test(test_function):
    threads = []
    start = time.time()

    for _ in range(NUM_THREADS):
        t = threading.Thread(target=test_function)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    end = time.time()
    print(f"\n🧪 Load Test Results:")
    print(f"  ✅ Success: {success}")
    print(f"  ❌ Failures: {fail}")
    print(f"  ⏱️ Time taken: {end - start:.2f} sec\n")

if __name__ == '__main__':
    print("🔁 Нагрузка на поиск по ключевому слову")
    run_load_test(test_keyword_search)

    # Сброс статистики
    success = 0
    fail = 0

    print("🔁 Нагрузка на поиск по жанру и году")
    run_load_test(test_genre_year_search)
