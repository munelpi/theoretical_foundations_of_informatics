"""Собственные реализации узловых структур данных для лабораторной работы №3."""


class Node:
    """Узел односвязного списка."""

    def __init__(self, value):
        self.value = value
        self.next = None


class LinkedList:
    """Односвязный список для хранения истории обслуживания."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, value):
        """Добавляет значение в конец списка за O(1)."""
        new_node = Node(value)
        if self.head is None:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def find(self, request_id):
        """Рекурсивно ищет заявку по номеру."""
        def search(node):
            if node is None:
                return None
            if node.value["номер"] == request_id:
                return node.value
            return search(node.next)
        return search(self.head)

    def to_list(self):
        """Рекурсивно возвращает значения в порядке следования узлов."""
        def collect(node):
            if node is None:
                return []
            return [node.value] + collect(node.next)
        return collect(self.head)

    def reverse(self):
        """Разворачивает список, изменяя ссылки next."""
        previous = None
        current = self.head
        self.tail = self.head
        while current is not None:
            next_node = current.next
            current.next = previous
            previous = current
            current = next_node
        self.head = previous

    def __len__(self):
        return self.size

    def __repr__(self):
        return f"LinkedList({self.to_list()!r})"


class Stack:
    """Стек на узлах: последний добавленный элемент извлекается первым."""

    def __init__(self):
        self.top = None
        self.size = 0

    def push(self, value):
        """Добавляет элемент на вершину стека за O(1)."""
        node = Node(value)
        node.next = self.top
        self.top = node
        self.size += 1

    def pop(self):
        """Снимает вершину стека; для пустого стека выбрасывает IndexError."""
        if self.top is None:
            raise IndexError("стек пуст")
        value = self.top.value
        self.top = self.top.next
        self.size -= 1
        return value

    def is_empty(self):
        return self.top is None

    def __len__(self):
        return self.size

    def __repr__(self):
        values = []
        current = self.top
        while current is not None:
            values.append(current.value)
            current = current.next
        return f"Stack({values!r})"


class Queue:
    """Очередь на узлах с добавлением в хвост и извлечением из головы."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def enqueue(self, value):
        """Добавляет элемент в хвост очереди за O(1)."""
        node = Node(value)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.size += 1

    def dequeue(self):
        """Извлекает первый элемент; для пустой очереди выбрасывает IndexError."""
        if self.head is None:
            raise IndexError("очередь пуста")
        value = self.head.value
        self.head = self.head.next
        if self.head is None:
            self.tail = None
        self.size -= 1
        return value

    def remove_value(self, request_id):
        """Удаляет заявку по номеру, сохраняя связи между оставшимися узлами."""
        previous = None
        current = self.head
        while current is not None:
            if current.value["номер"] == request_id:
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next
                if current is self.tail:
                    self.tail = previous
                self.size -= 1
                if self.head is None:
                    self.tail = None
                return True
            previous = current
            current = current.next
        return False

    def to_list(self):
        """Возвращает элементы очереди в порядке обслуживания."""
        result = []
        current = self.head
        while current is not None:
            result.append(current.value)
            current = current.next
        return result

    def is_empty(self):
        return self.head is None

    def __len__(self):
        return self.size

    def __repr__(self):
        return f"Queue({self.to_list()!r})"


class HashTable:
    """Хэш-таблица на основе встроенного словаря."""

    def __init__(self):
        self._data = {}

    def insert(self, key, value):
        """Сохраняет значение по неизменяемому ключу."""
        if not isinstance(key, (int, str, tuple, frozenset)):
            raise TypeError("ключ должен быть неизменяемым")
        self._data[key] = value

    def get(self, key):
        """Возвращает значение или None, если ключ отсутствует."""
        return self._data.get(key)

    def __contains__(self, key):
        return key in self._data

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"HashTable({self._data!r})"
