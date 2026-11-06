"""Лабораторная работа №3. Обработка заявок сервисного центра."""
from copy import deepcopy
from data_structures import LinkedList, Queue, Stack, HashTable


VALID_TYPES = {"ремонт", "консультация", "установка"}
VALID_PRIORITIES = {"обычная", "срочная"}


def load_requests(filename):
    """Читает файл, проверяет записи и распределяет заявки по очередям."""
    normal_queue = Queue()
    urgent_queue = Queue()
    errors = []
    all_requests = HashTable()
    categories = set()
    valid_count = 0

    try:
        file = open(filename, "r", encoding="utf-8")
    except FileNotFoundError:
        return normal_queue, urgent_queue, errors + [f"Файл {filename!r} не найден."], 0, all_requests, categories

    with file:
        for line_number, raw_line in enumerate(file, start=1):
            line = raw_line.strip()
            if not line:
                continue
            fields = [field.strip() for field in line.split(";")]
            if len(fields) != 5:
                errors.append(f"Строка {line_number}: неверное количество полей.")
                continue

            request_id_text, client, request_type, category, priority = fields
            if not request_id_text.isdigit() or int(request_id_text) <= 0:
                errors.append(f"Строка {line_number}: номер заявки должен быть положительным целым числом.")
                continue
            request_id = int(request_id_text)
            if request_id in all_requests:
                errors.append(f"Строка {line_number}: повторяющийся номер заявки {request_id}.")
                continue
            if not client:
                errors.append(f"Строка {line_number}: пустое имя клиента.")
                continue
            if request_type not in VALID_TYPES:
                errors.append(f"Строка {line_number}: неизвестный тип заявки: {request_type!r}.")
                continue
            if not category:
                errors.append(f"Строка {line_number}: пустая категория.")
                continue
            if priority not in VALID_PRIORITIES:
                errors.append(f"Строка {line_number}: неизвестный приоритет: {priority!r}.")
                continue

            request = {
                "номер": request_id,
                "порядок поступления": valid_count + 1,
                "клиент": client,
                "тип": request_type,
                "категория": category,
                "приоритет": priority,
            }
            all_requests.insert(request_id, request)
            categories.add(category)
            if priority == "срочная":
                urgent_queue.enqueue(request)
            else:
                normal_queue.enqueue(request)
            valid_count += 1

    return normal_queue, urgent_queue, errors, valid_count, all_requests, categories


def serve_request(normal_queue, urgent_queue, history, stack, served_order):
    """Обслуживает срочную заявку при её наличии, иначе обычную."""
    if not urgent_queue.is_empty():
        request = urgent_queue.dequeue()
    elif not normal_queue.is_empty():
        request = normal_queue.dequeue()
    else:
        return None
    history.append(request)
    served_order[request["номер"]] = len(served_order) + 1
    return request


def cancel_request(request_id, normal_queue, urgent_queue, stack):
    """Удаляет заявку из очередей и стека принятых заявок."""
    removed = urgent_queue.remove_value(request_id)
    if not removed:
        removed = normal_queue.remove_value(request_id)
    if not removed:
        return False

    # Стек перестраивается через временный стек, чтобы убрать отменённый номер.
    temporary = Stack()
    while not stack.is_empty():
        value = stack.pop()
        if value != request_id:
            temporary.push(value)
    while not temporary.is_empty():
        stack.push(temporary.pop())
    return True


def cancel_last_accepted(stack, normal_queue, urgent_queue):
    """Отменяет последнюю принятую заявку, если она ещё ожидает."""
    if stack.is_empty():
        return None
    request_id = stack.pop()
    removed = urgent_queue.remove_value(request_id)
    if not removed:
        removed = normal_queue.remove_value(request_id)
    return request_id if removed else None


def find_in_history_recursive(node, request_id):
    """Рекурсивно ищет заявку в узлах истории."""
    if node is None:
        return None
    if node.value["номер"] == request_id:
        return node.value
    return find_in_history_recursive(node.next, request_id)


def calculate_statistics(requests, served_order):
    """Считает количество и учебное время ожидания по типам заявок."""
    stats = {}
    for request_type in sorted(VALID_TYPES):
        selected = [r for r in requests if r["тип"] == request_type]
        waits = [
            max(0, served_order[r["номер"]] - r["порядок поступления"])
            for r in selected if r["номер"] in served_order
        ]
        stats[request_type] = {
            "количество": len(selected),
            "срочных": sum(r["приоритет"] == "срочная" for r in selected),
            "среднее ожидание": sum(waits) / len(waits) if waits else 0,
            "максимальное ожидание": max(waits) if waits else 0,
        }
    return stats


def save_report(filename, valid_count, errors, categories, stats, history):
    """Сохраняет сводный отчёт в текстовый файл."""
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"Количество корректных записей: {valid_count}\n")
        file.write(f"Количество некорректных записей: {len(errors)}\n\n")
        file.write("Уникальные категории:\n")
        for category in sorted(categories):
            file.write(f"- {category}\n")
        file.write("\nСтатистика по типам заявок:\n")
        for request_type, values in stats.items():
            file.write(
                f"{request_type}: всего {values['количество']}, срочных {values['срочных']}, "
                f"среднее ожидание {values['среднее ожидание']:.2f}, "
                f"максимальное ожидание {values['максимальное ожидание']}\n"
            )
        file.write("\nОбслуженные заявки:\n")
        for request in history:
            file.write(
                f"{request['номер']};{request['клиент']};{request['тип']};"
                f"{request['категория']};{request['приоритет']}\n"
            )
        file.write("\nОшибки входных данных:\n")
        for error in errors:
            file.write(error + "\n")


def run_tests():
    """Выполняет автоматические проверки основных операций."""
    queue = Queue()
    sample_a = {"номер": 1}
    sample_b = {"номер": 2}
    queue.enqueue(sample_a)
    assert queue.dequeue() == sample_a
    assert queue.is_empty()

    queue.enqueue(sample_a)
    queue.enqueue(sample_b)
    assert queue.remove_value(1) is True
    assert queue.to_list() == [sample_b]
    assert queue.remove_value(99) is False

    try:
        Queue().dequeue()
        assert False
    except IndexError:
        assert True

    try:
        Stack().pop()
        assert False
    except IndexError:
        assert True

    stack = Stack()
    stack.push(1)
    stack.push(2)
    assert stack.pop() == 2

    linked = LinkedList()
    linked.append(sample_a)
    linked.append(sample_b)
    assert linked.to_list() == [sample_a, sample_b]
    linked.reverse()
    assert linked.to_list() == [sample_b, sample_a]

    normal = Queue()
    urgent = Queue()
    normal.enqueue({"номер": 10})
    urgent.enqueue({"номер": 11})
    history = LinkedList()
    assert serve_request(normal, urgent, history, Stack(), {})["номер"] == 11

    table = HashTable()
    table.insert(123, "заявка")
    assert table.get(123) == "заявка"
    assert table.get(999) is None

    original = [1, 2, 3]
    copied = deepcopy(original)
    assert original == [1, 2, 3] and copied is not original
    assert len(LinkedList()) == 0
    print("Автоматические проверки пройдены.")


def print_queue(title, queue):
    print(title)
    if queue.is_empty():
        print("  (пусто)")
    else:
        for request in queue.to_list():
            print(f"  {request['номер']} — {request['клиент']} ({request['тип']}, {request['приоритет']})")


def main():
    """Запускает консольное меню программы."""
    run_tests()
    normal_queue, urgent_queue, errors, valid_count, request_table, categories = load_requests("input.txt")
    history = LinkedList()
    accepted_stack = Stack()
    served_order = {}
    all_valid_requests = [request_table.get(key) for key in request_table._data]

    # Стек содержит все принятые и ещё не обслуженные заявки.
    for request in all_valid_requests:
        accepted_stack.push(request["номер"])

    while True:
        print("\n=== Сервисный центр ===")
        print("1. Показать заявки в очередях")
        print("2. Обслужить заявку")
        print("3. Отменить заявку по номеру")
        print("4. Отменить последнюю принятую заявку")
        print("5. Показать историю обслуживания")
        print("6. Развернуть историю")
        print("7. Показать статистику")
        print("8. Найти заявку по номеру")
        print("9. Сохранить отчёт")
        print("0. Завершить программу")
        choice = input("Выберите пункт: ").strip()

        if choice == "1":
            print_queue("Срочная очередь:", urgent_queue)
            print_queue("Обычная очередь:", normal_queue)
        elif choice == "2":
            request = serve_request(normal_queue, urgent_queue, history, accepted_stack, served_order)
            if request is None:
                print("Нет заявок для обслуживания.")
            else:
                print(f"Обслужена заявка №{request['номер']} — {request['клиент']}.")
                # Убираем обслуженную заявку из стека ожидающих.
                temporary = Stack()
                while not accepted_stack.is_empty():
                    number = accepted_stack.pop()
                    if number != request["номер"]:
                        temporary.push(number)
                while not temporary.is_empty():
                    accepted_stack.push(temporary.pop())
        elif choice == "3":
            try:
                number = int(input("Введите номер заявки: "))
                if cancel_request(number, normal_queue, urgent_queue, accepted_stack):
                    print("Заявка отменена.")
                else:
                    print("Заявка не найдена в очередях.")
            except ValueError:
                print("Номер должен быть целым числом.")
        elif choice == "4":
            number = cancel_last_accepted(accepted_stack, normal_queue, urgent_queue)
            if number is None:
                print("Нет ожидающих заявок для отмены.")
            else:
                print(f"Отменена последняя принятая заявка №{number}.")
        elif choice == "5":
            print("История:", history)
        elif choice == "6":
            history.reverse()
            print("История развёрнута.")
        elif choice == "7":
            stats = calculate_statistics(all_valid_requests, served_order)
            for request_type, values in stats.items():
                print(
                    f"{request_type}: всего {values['количество']}, срочных {values['срочных']}, "
                    f"среднее ожидание {values['среднее ожидание']:.2f}, "
                    f"максимальное ожидание {values['максимальное ожидание']}"
                )
        elif choice == "8":
            try:
                number = int(input("Введите номер заявки: "))
                request = request_table.get(number)
                if request is None:
                    request = find_in_history_recursive(history.head, number)
                print(request if request is not None else "Заявка не найдена.")
            except ValueError:
                print("Номер должен быть целым числом.")
        elif choice == "9":
            stats = calculate_statistics(all_valid_requests, served_order)
            save_report("report.txt", valid_count, errors, categories, stats, history.to_list())
            print("Отчёт сохранён в report.txt.")
        elif choice == "0":
            print("Работа программы завершена.")
            break
        else:
            print("Неизвестный пункт меню. Повторите ввод.")


if __name__ == "__main__":
    main()
