from tabulate import tabulate

def print_results(results, start_index=1):
    """
    Выводит результаты в табличном виде.
    results — список словарей с ключами: title, year, description.
    """
    table = []
    for i, item in enumerate(results, start=start_index):
        title = item.get("title", "—")
        year = item.get("year", "—")
        desc = item.get("description", item.get("desc", "—"))
        table.append([i, title, year, desc])

    headers = ["№", "Название", "Год", "Описание"]
    print(tabulate(table, headers=headers, tablefmt="grid"))

