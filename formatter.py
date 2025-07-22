def print_results(results):
    if not results:
        print("Нет результатов.")
        return
    for idx, row in enumerate(results, 1):
        print(f"{idx}. {row[0]} ({row[1]})")
        print(f"   {row[2][:100]}...\n")  # краткое описание
