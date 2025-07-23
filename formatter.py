from tabulate import tabulate

# 📋 Форматированный табличный вывод фильмов
def print_results(results):
    if not results:
        print("⚠️ Нет результатов.\n")
        return

    headers = ["#", "Название", "Год", "Описание (обрезано до 100 символов)"]

    # Формируем строки таблицы: обрезаем длинные описания
    table = [
        [i + 1, title, year, (desc[:100] + "...") if desc and len(desc) > 100 else desc]
        for i, (title, year, desc) in enumerate(results)
    ]

    print(tabulate(table, headers=headers, tablefmt="grid"))
    print()  # отступ
