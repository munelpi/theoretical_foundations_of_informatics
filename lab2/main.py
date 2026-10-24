"""
Лабораторная работа №2. Вариант 2: Анализ заказов магазина.
Процедурная программа обработки данных.
"""

import os

ALLOWED_STATUSES = ("новый", "в обработке", "выполнен", "отменён")

INPUT_FILE = "orders.txt"
REPORT_FILE = "orders_report.txt"


def read_lines(file_path):
    """Читает файл и возвращает список непустых строк."""
    if not os.path.exists(file_path):
        print(f"Ошибка: файл '{file_path}' не найден.")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f]
    except OSError as exc:
        print(f"Ошибка чтения файла: {exc}")
        return []

    return [line for line in lines if line]


def parse_line(line):
    """Разбирает строку на поля. Возвращает список или None."""
    parts = [p.strip() for p in line.split(";")]
    if len(parts) != 6:
        return None
    return parts


def validate_record(fields, seen_ids):
    """Проверяет запись. Возвращает (order, err)."""
    if fields is None:
        return None, "неправильное количество полей (ожидается 6)"

    num_str, customer, category, qty_str, price_str, status = fields

    if not num_str:
        return None, "пустое обязательное поле (номер заказа)"
    try:
        order_id = int(num_str)
    except ValueError:
        return None, f"номер заказа не является целым числом: «{num_str}»"
    if order_id <= 0:
        return None, "номер заказа должен быть положительным"

    if order_id in seen_ids:
        return None, f"повторяющийся номер заказа {order_id}"

    if not customer:
        return None, "пустое обязательное поле (имя покупателя)"

    if not category:
        return None, "пустое обязательное поле (категория товара)"

    try:
        quantity = int(qty_str)
    except ValueError:
        return None, f"количество не является целым числом: «{qty_str}»"
    if quantity <= 0:
        return None, "количество должно быть положительным"

    try:
        price = float(price_str)
    except ValueError:
        return None, f"цена не является числом: «{price_str}»"
    if price <= 0:
        return None, "цена должна быть положительной"

    status_norm = status.strip().lower()
    if status_norm not in ALLOWED_STATUSES:
        return None, f"неизвестный статус «{status}»"

    order = {
        "id": order_id,
        "customer": customer,
        "category": category,
        "quantity": quantity,
        "price": price,
        "status": status_norm,
    }
    return order, None


def load_orders(file_path):
    """Загружает заказы из файла. Возвращает (orders, errors)."""
    lines = read_lines(file_path)
    orders = []
    errors = []
    seen_ids = set()

    for idx, line in enumerate(lines, start=1):
        fields = parse_line(line)
        order, err = validate_record(fields, seen_ids)
        if order is not None:
            orders.append(order)
            seen_ids.add(order["id"])
        else:
            errors.append(f"Строка {idx}: {err}")

    return orders, errors


def calc_order_cost(order):
    """Стоимость заказа: C = q * p."""
    return order["quantity"] * order["price"]


def determine_category(cost):
    """Определяет категорию стоимости заказа."""
    if cost < 1000:
        return "Малый"
    elif cost < 5000:
        return "Средний"
    else:
        return "Крупный"


def enrich_orders(orders):
    """Возвращает новый список с добавленными cost и cost_category."""
    result = []
    for order in orders:
        cost = calc_order_cost(order)
        new_order = dict(order)
        new_order["cost"] = cost
        new_order["cost_category"] = determine_category(cost)
        result.append(new_order)
    return result


def filter_by_status(orders, status):
    """Фильтр по статусу (без учёта регистра)."""
    status_norm = status.strip().lower()
    return [o for o in orders if o["status"] == status_norm]


def filter_by_category(orders, category):
    """Фильтр по категории (без учёта регистра)."""
    cat_norm = category.strip().lower()
    return [o for o in orders if o["category"].lower() == cat_norm]


def search_by_customer(orders, part):
    """Поиск по части имени (без учёта регистра)."""
    part_norm = part.strip().lower()
    return [o for o in orders if part_norm in o["customer"].lower()]


def filter_large_orders(orders):
    """Заказы стоимостью >= 5000."""
    return [o for o in orders if o["cost"] >= 5000]


def sort_by_cost_desc(orders):
    """Сортировка по стоимости убыв., при равенстве — по номеру возр."""
    return sorted(orders, key=lambda o: (-o["cost"], o["id"]))


def sort_by_category_then_customer(orders):
    """Сортировка по категории возр., затем по имени покупателя возр."""
    return sorted(orders, key=lambda o: (o["category"].lower(), o["customer"].lower()))


def calc_revenue(orders):
    """Выручка: сумма стоимостей выполненных заказов."""
    return sum(o["cost"] for o in orders if o["status"] == "выполнен")


def calc_statistics_by_category(orders):
    """Статистика по категориям."""
    stats = {}
    for o in orders:
        cat = o["category"]
        if cat not in stats:
            stats[cat] = {"count": 0, "total_quantity": 0, "total_cost": 0.0, "done_cost": 0.0}
        stats[cat]["count"] += 1
        stats[cat]["total_quantity"] += o["quantity"]
        stats[cat]["total_cost"] += o["cost"]
        if o["status"] == "выполнен":
            stats[cat]["done_cost"] += o["cost"]

    for cat, s in stats.items():
        s["avg_cost"] = s["total_cost"] / s["count"] if s["count"] else 0.0
    return stats


def calc_statistics_by_status(orders):
    """Статистика по статусам. Все статусы присутствуют."""
    stats = {st: 0 for st in ALLOWED_STATUSES}
    for o in orders:
        stats[o["status"]] += 1
    return stats


def calc_general_indicators(orders):
    """Общие показатели."""
    total_count = len(orders)
    done_orders = [o for o in orders if o["status"] == "выполнен"]
    cancelled = [o for o in orders if o["status"] == "отменён"]

    total_cost = sum(o["cost"] for o in orders)
    revenue = sum(o["cost"] for o in done_orders)
    avg_cost = total_cost / total_count if total_count else 0.0
    most_expensive = max(orders, key=lambda o: o["cost"]) if orders else None

    customer_sums = {}
    for o in done_orders:
        customer_sums[o["customer"]] = customer_sums.get(o["customer"], 0.0) + o["cost"]

    best_customers = []
    if customer_sums:
        max_sum = max(customer_sums.values())
        best_customers = [name for name, s in customer_sums.items() if s == max_sum]

    return {
        "total_count": total_count,
        "done_count": len(done_orders),
        "cancelled_count": len(cancelled),
        "total_cost": total_cost,
        "revenue": revenue,
        "avg_cost": avg_cost,
        "most_expensive": most_expensive,
        "best_customers": best_customers,
        "best_customers_sum": max(customer_sums.values()) if customer_sums else 0.0,
    }


def format_order(o):
    """Форматирует одну запись."""
    return (f"{o['id']:>5} | {o['customer']:<20} | {o['category']:<14} | "
            f"{o['quantity']:>3} | {o['price']:>9.2f} | {o['cost']:>10.2f} | "
            f"{o['status']:<12} | {o['cost_category']}")


def print_orders(orders, title="Заказы"):
    """Выводит список заказов."""
    print(f"\n=== {title} ===")
    if not orders:
        print("Нет заказов для отображения.")
        return
    print(f"{'№':>5} | {'Покупатель':<20} | {'Категория':<14} | "
          f"{'Кол':>3} | {'Цена':>9} | {'Стоимость':>10} | "
          f"{'Статус':<12} | Категория стоимости")
    print("-" * 120)
    for o in orders:
        print(format_order(o))


def print_statistics(orders):
    """Выводит статистику."""
    print("\n=== Статистика по категориям товаров ===")
    cat_stats = calc_statistics_by_category(orders)
    if not cat_stats:
        print("Нет данных.")
    else:
        for cat in sorted(cat_stats.keys()):
            s = cat_stats[cat]
            print(f"{cat}:")
            print(f"  Количество заказов: {s['count']}")
            print(f"  Всего единиц товара: {s['total_quantity']}")
            print(f"  Общая стоимость: {s['total_cost']:.2f}")
            print(f"  Стоимость выполненных: {s['done_cost']:.2f}")
            print(f"  Средняя стоимость заказа: {s['avg_cost']:.2f}")

    print("\n=== Статистика по статусам ===")
    status_stats = calc_statistics_by_status(orders)
    for st in ALLOWED_STATUSES:
        print(f"  {st}: {status_stats[st]}")

    print("\n=== Общие показатели ===")
    g = calc_general_indicators(orders)
    print(f"  Всего заказов: {g['total_count']}")
    print(f"  Выполненных: {g['done_count']}")
    print(f"  Отменённых: {g['cancelled_count']}")
    print(f"  Общая стоимость: {g['total_cost']:.2f}")
    print(f"  Выручка: {g['revenue']:.2f}")
    print(f"  Средняя стоимость заказа: {g['avg_cost']:.2f}")
    if g["most_expensive"]:
        me = g["most_expensive"]
        print(f"  Самый дорогой заказ: №{me['id']} — {me['cost']:.2f}")
    if g["best_customers"]:
        print(f"  Лучший покупатель (сумма {g['best_customers_sum']:.2f}):")
        for name in g["best_customers"]:
            print(f"    - {name}")
    else:
        print("  Лучший покупатель: невозможно определить.")


def print_unique_categories(orders):
    """Уникальные категории через множество."""
    cats = {o["category"] for o in orders}
    print("\n=== Уникальные категории товаров ===")
    for c in sorted(cats):
        print(f"  {c}")


def build_report(orders, errors):
    """Формирует текст отчёта."""
    lines = []
    lines.append("=" * 60)
    lines.append("ОТЧЁТ ПО ЗАКАЗАМ МАГАЗИНА")
    lines.append("=" * 60)

    lines.append(f"\n1. Количество корректных записей: {len(orders)}")
    lines.append(f"2. Количество некорректных записей: {len(errors)}")

    cats = sorted({o["category"] for o in orders})
    lines.append("\n3. Уникальные категории товаров:")
    for c in cats:
        lines.append(f"   - {c}")

    lines.append("\n4. Заказы по убыванию стоимости:")
    for o in sort_by_cost_desc(orders):
        lines.append("   " + format_order(o))

    lines.append("\n5. Крупные заказы (стоимость >= 5000):")
    large = filter_large_orders(orders)
    if large:
        for o in large:
            lines.append("   " + format_order(o))
    else:
        lines.append("   Нет крупных заказов.")

    lines.append("\n6. Общие показатели:")
    g = calc_general_indicators(orders)
    lines.append(f"   Всего заказов: {g['total_count']}")
    lines.append(f"   Выполненных: {g['done_count']}")
    lines.append(f"   Отменённых: {g['cancelled_count']}")
    lines.append(f"   Общая стоимость: {g['total_cost']:.2f}")
    lines.append(f"   Выручка: {g['revenue']:.2f}")
    lines.append(f"   Средняя стоимость заказа: {g['avg_cost']:.2f}")
    if g["most_expensive"]:
        me = g["most_expensive"]
        lines.append(f"   Самый дорогой заказ: №{me['id']} — {me['cost']:.2f}")
    if g["best_customers"]:
        lines.append(f"   Лучший покупатель: {', '.join(g['best_customers'])} "
                     f"(сумма {g['best_customers_sum']:.2f})")

    lines.append("\n7. Статистика по категориям товаров:")
    cat_stats = calc_statistics_by_category(orders)
    for cat in sorted(cat_stats.keys()):
        s = cat_stats[cat]
        lines.append(f"   {cat}:")
        lines.append(f"     Заказов: {s['count']}, единиц: {s['total_quantity']}, "
                     f"общая: {s['total_cost']:.2f}, "
                     f"выполнено: {s['done_cost']:.2f}, "
                     f"средняя: {s['avg_cost']:.2f}")

    lines.append("\n8. Статистика по статусам:")
    status_stats = calc_statistics_by_status(orders)
    for st in ALLOWED_STATUSES:
        lines.append(f"   {st}: {status_stats[st]}")

    lines.append("\n9. Список ошибок входных данных:")
    if errors:
        for e in errors:
            lines.append(f"   {e}")
    else:
        lines.append("   Ошибок не обнаружено.")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def save_report(report_text, file_path):
    """Сохраняет отчёт в файл."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"Отчёт сохранён в файл '{file_path}'.")
    except OSError as exc:
        print(f"Ошибка сохранения отчёта: {exc}")


def show_menu():
    """Выводит консольное меню."""
    print("\n" + "=" * 50)
    print("МЕНЮ")
    print("=" * 50)
    print("1. Показать все заказы")
    print("2. Показать заказы по убыванию стоимости")
    print("3. Показать заказы по категориям")
    print("4. Найти заказы по статусу")
    print("5. Найти заказы по категории")
    print("6. Найти заказы покупателя")
    print("7. Показать крупные заказы")
    print("8. Показать статистику")
    print("9. Сохранить отчёт")
    print("0. Завершить программу")


def handle_menu(orders, errors):
    """Главный цикл меню."""
    while True:
        show_menu()
        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            print_orders(orders, "Все заказы")
        elif choice == "2":
            print_orders(sort_by_cost_desc(orders), "Заказы по убыванию стоимости")
        elif choice == "3":
            print_orders(sort_by_category_then_customer(orders),
                         "Заказы по категориям (внутри — по имени)")
        elif choice == "4":
            status = input("Введите статус: ").strip()
            found = filter_by_status(orders, status)
            if found:
                print_orders(found, f"Заказы со статусом «{status.strip()}»")
            else:
                print(f"Заказы со статусом «{status.strip()}» не найдены.")
        elif choice == "5":
            category = input("Введите категорию товара: ").strip()
            found = filter_by_category(orders, category)
            if found:
                print_orders(found, f"Заказы в категории «{category.strip()}»")
            else:
                print(f"Заказы в категории «{category.strip()}» не найдены.")
        elif choice == "6":
            part = input("Введите часть имени покупателя: ").strip()
            found = search_by_customer(orders, part)
            if found:
                print_orders(found, f"Заказы покупателя (поиск: «{part.strip()}»)")
            else:
                print(f"Заказы покупателя с «{part.strip()}» не найдены.")
        elif choice == "7":
            print_orders(filter_large_orders(orders), "Крупные заказы (>= 5000)")
        elif choice == "8":
            print_statistics(orders)
            print_unique_categories(orders)
        elif choice == "9":
            report = build_report(orders, errors)
            save_report(report, REPORT_FILE)
        elif choice == "0":
            print("Завершение программы.")
            break
        else:
            print("Неизвестный пункт меню. Попробуйте снова.")


def run_assertions():
    """Автоматические проверки (не менее шести)."""
    o = {
        "id": 1, "customer": "Тест", "category": "Книги",
        "quantity": 2, "price": 500.0, "status": "выполнен",
    }

    assert calc_order_cost(o) == 1000.0

    assert determine_category(0) == "Малый"
    assert determine_category(999.99) == "Малый"
    assert determine_category(1000) == "Средний"
    assert determine_category(4999.99) == "Средний"
    assert determine_category(5000) == "Крупный"
    assert determine_category(12000) == "Крупный"

    orders = [
        {**o, "id": 1, "status": "выполнен"},
        {**o, "id": 2, "status": "новый"},
        {**o, "id": 3, "status": "выполнен"},
    ]
    assert len(filter_by_status(orders, "ВЫПОЛНЕН")) == 2

    orders2 = [
        {**o, "id": 1, "category": "Книги"},
        {**o, "id": 2, "category": "Электроника"},
        {**o, "id": 3, "category": "книги"},
    ]
    assert len(filter_by_category(orders2, "КНИГИ")) == 2

    orders3 = [
        {**o, "id": 1, "customer": "Иванов Иван"},
        {**o, "id": 2, "customer": "Петрова Анна"},
        {**o, "id": 3, "customer": "Иванченко Пётр"},
    ]
    assert len(search_by_customer(orders3, "иван")) == 2

    orders4 = [
        {**o, "id": 3, "cost": 100.0},
        {**o, "id": 1, "cost": 500.0},
        {**o, "id": 2, "cost": 500.0},
        {**o, "id": 4, "cost": 50.0},
    ]
    assert [x["id"] for x in sort_by_cost_desc(orders4)] == [1, 2, 3, 4]

    orders5 = [
        {**o, "id": 1, "cost": 1000.0, "status": "выполнен"},
        {**o, "id": 2, "cost": 2000.0, "status": "новый"},
        {**o, "id": 3, "cost": 3000.0, "status": "выполнен"},
    ]
    assert calc_revenue(orders5) == 4000.0

    g = calc_general_indicators([])
    assert g["total_count"] == 0 and g["revenue"] == 0.0

    print("Все автоматические проверки пройдены успешно.")


def main():
    """Точка входа."""
    print("Лабораторная работа №2. Вариант 2: Анализ заказов магазина.")

    run_assertions()

    orders, errors = load_orders(INPUT_FILE)
    print(f"\nЗагружено корректных записей: {len(orders)}")
    print(f"Обнаружено ошибок: {len(errors)}")

    if errors:
        print("Ошибки входных данных:")
        for e in errors:
            print(f"  {e}")

    if not orders:
        print("\nВнимание: корректных записей нет. Работа с данными невозможна.")
        print("Будет сформирован отчёт с пустыми разделами.")

    enriched = enrich_orders(orders)
    handle_menu(enriched, errors)


if __name__ == "__main__":
    main()