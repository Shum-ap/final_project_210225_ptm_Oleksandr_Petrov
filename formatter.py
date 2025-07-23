from tabulate import tabulate

def print_results(results):
    if not results:
        print("⚠️ Нет результатов.\n")
        return

    headers = ["#", "Название", "Год", "Описание (обрезано до 100 символов)"]
    table = [
        [i + 1, title, year, (desc[:100] + "...") if desc and len(desc) > 100 else desc]
        for i, (title, year, desc) in enumerate(results)
    ]

    print(tabulate(table, headers=headers, tablefmt="grid"))
    print()  # Пустая строка для отступа
