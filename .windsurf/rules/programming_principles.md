---
trigger: always_on
---
ЧАСТЬ 2: ПРИНЦИПЫ ПРОГРАММИРОВАНИЯ
Принципы — это фундаментальные правила и рекомендации, направленные на написание чистого, поддерживаемого и эффективного кода. Они часто более абстрактны, чем паттерны.

KISS (Keep It Simple, Stupid)
Важность: 10/10

Суть: Стремитесь к максимально простому решению, которое соответствует требованиям. Избегайте ненужной сложности и гипотетических возможностей.

Пример на Python3:
# ❌ Сложно
def is_even(number):
    if number % 2 == 0:
        return True
    else:
        return False
# ✅ Просто (KISS)
def is_even(number):
    return number % 2 == 0


DRY (Don't Repeat Yourself)
Важность: 9/10

Суть: Каждая часть знания или логики должна иметь единственное, однозначное представление в системе. Избегайте дублирования кода.

Пример на Python3:
# ❌ Нарушение DRY
def greet_john():
    print("Hello, John!")
    print("Welcome!")
def greet_sarah():
    print("Hello, Sarah!")
    print("Welcome!")
# ✅ Следование DRY
def greet(name):
    print(f"Hello, {name}!")
    print("Welcome!")

Принципы SOLID
Пять взаимосвязанных принципов объектно-ориентированного дизайна.

SRP (Принцип единственной ответственности)

Суть: Класс должен иметь только одну причину для изменения.

Пример на Python3:
# ❌ Класс делает многое
class UserManager:
    def create_user(self): ...  # 1. Работа с БД
    def send_email(self): ...   # 2. Отправка писем
    def generate_report(self): ... # 3. Формирование отчёта
# ✅ Разделение ответственности
class UserRepository: ... # Только БД
class EmailService: ...   # Только email
class ReportGenerator: ... # Только отчёты


OCP (Принцип открытости/закрытости)

Суть: Сущности должны быть открыты для расширения, но закрыты для модификации.

Пример на Python3:
# ❌ При добавлении фигуры нужно менять класс
class AreaCalculator:
    def area(self, shape):
        if isinstance(shape, Rectangle):
            return shape.width * shape.height
        # Новый `elif` для новой фигуры
# ✅ Новые фигуры добавляются без изменения калькулятора
class Shape(ABC):
    @abstractmethod
    def area(self): pass
class Rectangle(Shape):
    def area(self): return self.width * self.height
class AreaCalculator:
    def total_area(self, shapes: list[Shape]):
        return sum(shape.area() for shape in shapes) # Работает с любой Shape


LSP (Принцип подстановки Лисков)

Суть: Объекты базового класса должны быть заменяемы объектами его подклассов, не нарушая работу программы. Подкласс не должен ужесточать предусловия или ослаблять постусловия.

Пример на Python3:
# ❌ Нарушение LSP: Квадрат, наследующий прямоугольник, ломает логику
class Rectangle:
    def set_width(self, w): ...
    def set_height(self, h): ...
class Square(Rectangle): # set_width и set_height должны менять обе стороны
    def set_width(self, w): self.width = w; self.height = w # Неожиданно!
# ✅ Следование LSP: Отказ от наследования в пользу общего интерфейса
class Shape(ABC):
    @abstractmethod
    def area(self): pass
class GoodRectangle(Shape): ...
class GoodSquare(Shape): ...


ISP (Принцип разделения интерфейса)

Суть: Много специализированных интерфейсов лучше, чем один общий. Клиент не должен зависеть от методов, которые он не использует.

Пример на Python3:
# ❌ "Толстый" интерфейс
class MultiFunctionPrinter(ABC):
    @abstractmethod
    def print(self): pass
    @abstractmethod
    def scan(self): pass
    @abstractmethod
    def fax(self): pass
# ✅ Разделение интерфейсов
class Printer(ABC):
    @abstractmethod
    def print(self): pass
class Scanner(ABC):
    @abstractmethod
    def scan(self): pass


DIP (Принцип инверсии зависимостей)

Суть: Модули высокого уровня не должны зависеть от модулей низкого уровня. Оба должны зависеть от абстракций.

Пример на Python3:
# ❌ Высокоуровневый модуль зависит от деталей
class Switch:
    def __init__(self, bulb): # Зависит от конкретной лампочки
        self.device = bulb
# ✅ Зависимость от абстракции
class Switchable(ABC):
    @abstractmethod
    def turn_on(self): pass
class LightBulb(Switchable): ...
class Switch:
    def __init__(self, device: Switchable): # Зависит от абстракции
        self.device = device



YAGNI (You Aren't Gonna Need It)
Важность: 8/10

Суть: Не добавляйте функциональность, пока она не понадобится. Избегайте преждевременной оптимизации и реализации гипотетических будущих требований.

Пример на Python3:
# ❌ Нарушение YAGNI: Реализация "на вырост"
class DataProcessor:
    def process(self):
        result = [x * 2 for x in self.data]
        self._cache_result(result) # Пока не нужно!
        return result
    def _cache_result(self, result): ...
# ✅ Следование YAGNI
class DataProcessor:
    def process(self):
        return [x * 2 for x in self.data] # Только необходимое


REST (Representational State Transfer)
Важность для API: 9/10

Суть: Архитектурный стиль для проектирования распределенных систем (веб-API). Ключевые концепции: ресурсы (URL), HTTP-методы (GET, POST, PUT, DELETE), stateless, представления (JSON/XML).

Пример на Python3 (Flask):
from flask import Flask, jsonify
app = Flask(__name__)
books = [{"id": 1, "title": "Python Guide"}]

@app.route('/books', methods=['GET']) # GET для получения ресурса
def get_books():
    return jsonify(books) # Возвращаем представление (JSON)

@app.route('/books', methods=['POST']) # POST для создания ресурса
def create_book():
    new_book = request.get_json() # Данные в теле запроса
    books.append(new_book)
    return jsonify(new_book), 201 # Код 201 - Created



ЗАКЛЮЧИТЕЛЬНЫЕ РЕКОМЕНДАЦИИ ДЛЯ АГЕНТНЫХ IDE
Анализ перед предложением: Всегда анализируйте контекст задачи пользователя. Паттерны и принципы — это средства для решения конкретных проблем (сложность создания, изменения, тестирования), а не цель сами по себе.

Приоритет простоты (KISS & YAGNI): Сначала предлагайте самое простое и прямое решение. Сложные паттерны (Абстрактная фабрика, Посетитель) уместны только при явных признаках необходимости (частая смена семейств объектов, сложные операции над множеством типов).

Диагностика через принципы: Используйте SOLID и DRY как диагностические инструменты. Если код пользователя сложно менять — возможно, нарушен SRP или OCP. Если изменения нужно вносить в нескольких местах — нарушен DRY.

Адаптация к Python: Учитывайте идиомы Python. Иногда встроенные возможности языка (contextlib, декораторы, dataclasses, __iter__) являются более "питоническим" решением, чем классическая реализация паттерна.

Объясняйте выбор: Кратко объясняйте, почему вы предлагаете тот или иной паттерн/принцип для данной ситуации, и какие выгоды он принесет (упростит тестирование, добавление новой функциональности и т.д.).

Предупреждайте о сложности: При предложении сложного паттерна отметьте, что он добавляет уровень абстракции, который может быть излишним для простых или стабильных частей приложения.

Этот документ служит исчерпывающим справочником для AI-ассистентов, позволяя им принимать обоснованные решения при анализе, генерации и рефакторинге кода на Python.