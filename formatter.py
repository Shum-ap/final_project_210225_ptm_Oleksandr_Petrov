# formatter.py
from tabulate import tabulate


def format_table(results, page=1, total=0, limit=10):
    """
    Форматирует список результатов в виде таблицы.
    Обрезает длинные описания и добавляет нумерацию.

    :param results: Список кортежей (название, год, описание)
    :param page: Номер текущей страницы
    :param total: Общее количество результатов
    :param limit: Количество результатов на странице
    :return: Строка с форматированной таблицей
    """
    start_idx = (page - 1) * limit
    headers = ["№", "Название", "Год", "Описание"]
    table = []

    for i, item in enumerate(results, start=start_idx + 1):
        if isinstance(item, (list, tuple)) and len(item) >= 3:
            title, year, desc = str(item[0]), str(item[1]), str(item[2]) if item[2] else ""
            desc = (desc[:100] + "...") if len(desc) > 100 else desc
        else:
            title, year, desc = str(item), "", ""
        table.append([i, title, year, desc])

    # Формируем таблицу
    table_str = tabulate(table, headers=headers, tablefmt="grid")
    footer = f"\n📄 Страница {page} | Показано {min(len(results), limit)} из {total}"
    return table_str + footer