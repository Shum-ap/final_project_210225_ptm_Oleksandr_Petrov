from tabulate import tabulate

# 📋 Форматированный вывод фильмов с учётом общей нумерации
def print_results(results, start_index=1):
    if not results:
        print("⚠️ Нет результатов.\n")
        return

    headers = ["#", "Название", "Год", "Описание (до 100 символов)"]

    table = [
        [start_index + i, title, year, (desc[:100] + "...") if desc and len(desc) > 100 else desc]
        for i, (title, year, desc) in enumerate(results)
    ]

    print(tabulate(table, headers=headers, tablefmt="grid"))
    print()  # Пустая строка для отступа

