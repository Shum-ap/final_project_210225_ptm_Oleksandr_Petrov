from tabulate import tabulate

# 🖨️ Красивый вывод результатов
def print_results(results, start_index=1):
    """
    🖨️ Выводит результаты поиска в виде таблицы.
    Аргументы:
    - results: список словарей с ключами title, year, description (или desc)
    - start_index: начальный номер для нумерации
    """
    table = []
    for i, item in enumerate(results, start=start_index):
        title = item.get("title", "—")
        year = item.get("year", "—")
        desc = item.get("description") or item.get("desc", "—")
        table.append([i, title, year, desc])

    print(tabulate(table, headers=["№", "Название", "Год", "Описание"], tablefmt="grid"))
