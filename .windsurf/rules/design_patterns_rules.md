---
trigger: always_on
---
# Исчерпывающие правила для агентных IDE: Паттерны и принципы программирования

## Введение

Этот документ представляет собой комплексное руководство для агентных IDE (интегрированных сред разработки с искусственным интеллектом) по работе с классическими паттернами проектирования и фундаментальными принципами программирования.

**Цель** — помочь AI-ассистентам:

- Распознавать контекст, в котором применение паттерна или принципа уместно.
- Предлагать оптимальные решения, основанные на проверенных практиках.
- Корректно генерировать или рефакторить код на Python 3, следуя этим правилам.

**Структура документа:**

- **Часть 1: Паттерны проектирования** — сгруппированы по категориям, отсортированы по популярности.
- **Часть 2: Принципы программирования** — фундаментальные правила написания качественного кода.
- **Заключительные рекомендации** — для AI-агентов.

Каждый элемент сопровождается объяснением, оценкой важности и практическим примером на Python 3.

---

## ЧАСТЬ 1: ПАТТЕРНЫ ПРОЕКТИРОВАНИЯ

Паттерны — это типовые решения часто встречающихся проблем в проектировании ПО. Они представляют собой не готовый код, а концепцию, которую можно адаптировать под конкретную задачу.

---

### Порождающие паттерны (Creational Patterns)

Управляют процессом создания объектов, делая систему независимой от способа создания, композиции и представления объектов.

---

#### 1. Одиночка / Singleton

**Популярность:** 9/10  
**Суть:** Гарантирует, что у класса есть только один экземпляр, и предоставляет к нему глобальную точку доступа.

**Пример на Python3:**
```python
class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.value = None
        return cls._instance

obj1 = Singleton()
obj1.value = "Первый"
obj2 = Singleton()
print(obj2.value)  # Вывод: "Первый"
print(obj1 is obj2) # Вывод: True


#### 2. Фабричный метод / Factory Method

**Популярность:** 8/10  
**Суть:** Определяет интерфейс для создания объекта, но позволяет подклассам решать, какой класс инстанцировать.

**Пример на Python3:**
```python
from abc import ABC, abstractmethod

class Transport(ABC):
    @abstractmethod
    def deliver(self):
        pass

class Truck(Transport):
    def deliver(self):
        return "Доставка грузовиком."

class Ship(Transport):
    def deliver(self):
        return "Доставка кораблём."

class Logistics(ABC):
    @abstractmethod
    def create_transport(self) -> Transport:
        pass
    def plan_delivery(self):
        transport = self.create_transport()
        return transport.deliver()

class RoadLogistics(Logistics):
    def create_transport(self) -> Transport:
        return Truck()

road_log = RoadLogistics()
print(road_log.plan_delivery())  # Вывод: Доставка грузовиком.
```


#### 3. Строитель / Builder

**Популярность:** 8/10  
**Суть:** Позволяет создавать сложные объекты пошагово, используя один и тот же процесс строительства. Отделяет конструирование сложного объекта от его представления.

**Пример на Python3:**
```python
class Pizza:
    def __init__(self):
        self.toppings = []
    def add_topping(self, topping):
        self.toppings.append(topping)
        return self  # Fluent Interface
    def __str__(self):
        return f"Пицца с: {', '.join(self.toppings)}"

pizza = Pizza().add_topping("сыр").add_topping("грибы").add_topping("пепперони")
print(pizza)  # Вывод: Пицца с: сыр, грибы, пепперони
```

#### 4. Абстрактная фабрика / Abstract Factory

**Популярность:** 7/10  
**Суть:** Предоставляет интерфейс для создания семейств взаимосвязанных или взаимозависимых объектов, не специфицируя их конкретных классов.

**Пример на Python3:**
```python
from abc import ABC, abstractmethod

class Button(ABC):
    @abstractmethod
    def paint(self): pass

class WindowsButton(Button):
    def paint(self):
        return "Кнопка в стиле Windows"

class GUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button: pass

class WindowsFactory(GUIFactory):
    def create_button(self) -> Button:
        return WindowsButton()

def create_ui(factory: GUIFactory):
    button = factory.create_button()
    print(button.paint())

win_factory = WindowsFactory()
create_ui(win_factory)  # Вывод: Кнопка в стиле Windows
```


#### 5. Прототип / Prototype

**Популярность:** 6/10  
**Суть:** Позволяет создавать новые объекты путём копирования существующего объекта (прототипа), вместо создания через конструктор.

**Пример на Python3:**
```python
import copy

class Prototype:
    def __init__(self, value):
        self.value = value
        self.list = [1, 2, 3]

    def clone(self):
        return copy.deepcopy(self)

original = Prototype("оригинал")
cloned = original.clone()

cloned.value = "клон"
cloned.list.append(4)

print(original.value)  # Вывод: оригинал
print(original.list)   # Вывод: [1, 2, 3]
print(cloned.list)     # Вывод: [1, 2, 3, 4]
```


### Структурные паттерны (Structural Patterns)

Отвечают за построение удобных в поддержке иерархий классов, композицию объектов и обеспечение новых функциональных возможностей.

---

#### 6. Адаптер / Adapter

**Популярность:** 9/10  
**Суть:** Позволяет объектам с несовместимыми интерфейсами работать вместе. Является «мостом» между двумя интерфейсами.

**Пример на Python3:**
```python
class OldPrinter:
    def print_old(self, text):
        return f"Старая печать: {text}"

class NewPrinterInterface:
    def print_new(self, message): pass

class PrinterAdapter(NewPrinterInterface):
    def __init__(self, old_printer):
        self._old_printer = old_printer
    def print_new(self, message):
        return self._old_printer.print_old(message)

old = OldPrinter()
adapter = PrinterAdapter(old)
result = adapter.print_new("Новый текст")
print(result)  # Вывод: Старая печать: Новый текст
```


#### 7. Фасад / Facade

**Популярность:** 9/10  
**Суть:** Предоставляет простой интерфейс к сложной подсистеме классов, библиотеке или фреймворку. Скрывает сложность системы.

**Пример на Python3:**
```python
class SubsystemA:
    def operation_a(self):
        return "Подсистема A: Готово."

class SubsystemB:
    def operation_b(self):
        return "Подсистема B: Готово."

class Facade:
    def __init__(self):
        self._a = SubsystemA()
        self._b = SubsystemB()
    def simple_operation(self):
        results = []
        results.append(self._a.operation_a())
        results.append(self._b.operation_b())
        return "\n".join(results)

facade = Facade()
print(facade.simple_operation())
# Вывод:
# Подсистема A: Готово.
# Подсистема B: Готово.
```


#### 8. Декоратор / Decorator

**Популярность:** 8/10  
**Суть:** Динамически добавляет объекту новые обязанности. Является гибкой альтернативой порождению подклассов для расширения функциональности.

**Пример на Python3:**
```python
from abc import ABC, abstractmethod

class Component(ABC):
    @abstractmethod
    def operation(self) -> str: pass

class ConcreteComponent(Component):
    def operation(self) -> str:
        return "Конкретный компонент"

class Decorator(Component):
    _component: Component = None
    def __init__(self, component: Component):
        self._component = component
    def operation(self) -> str:
        return self._component.operation()

class ConcreteDecoratorA(Decorator):
    def operation(self) -> str:
        return f"Декоратор А ({self._component.operation()})"

simple = ConcreteComponent()
decorated = ConcreteDecoratorA(simple)
print(decorated.operation())  # Вывод: Декоратор А (Конкретный компонент)
```


#### 9. Заместитель / Proxy

**Популярность:** 8/10  
**Суть:** Позволяет подставлять вместо реальных объектов специальные объекты-заменители. Эти объекты перехватывают вызовы к оригинальному объекту, позволяя сделать что-то до или после передачи вызова.

**Пример на Python3:**
```python
from abc import ABC, abstractmethod

class Subject(ABC):
    @abstractmethod
    def request(self): pass

class RealSubject(Subject):
    def request(self):
        return "Запрос к RealSubject"

class Proxy(Subject):
    def __init__(self, real_subject: RealSubject):
        self._real_subject = real_subject
    def request(self):
        print("Прокси: Проверка доступа...")
        result = self._real_subject.request()
        print("Прокси: Логирование результата...")
        return result

real = RealSubject()
proxy = Proxy(real)
print(proxy.request())
# Вывод:
# Прокси: Проверка доступа...
# Прокси: Логирование результата...
# Запрос к RealSubject
```


#### 10. Компоновщик / Composite

**Популярность:** 7/10  
**Суть:** Объединяет объекты в древовидные структуры для представления иерархий «часть–целое». Позволяет клиентам единообразно трактовать как отдельные объекты, так и их композиции.

**Пример на Python3:**
```python
from abc import ABC, abstractmethod

class Component(ABC):
    @abstractmethod
    def operation(self):
        pass

class Leaf(Component):
    def __init__(self, name):
        self.name = name
    def operation(self):
        return f"Лист {self.name}"

class Composite(Component):
    def __init__(self, name):
        self.name = name
        self._children = []
    def add(self, component):
        self._children.append(component)
    def operation(self):
        results = [f"Узел {self.name}:"]
        for child in self._children:
            results.append(f"  - {child.operation()}")
        return "\n".join(results)

leaf1 = Leaf("1")
leaf2 = Leaf("2")
composite = Composite("A")
composite.add(leaf1)
composite.add(leaf2)
print(composite.operation())
# Вывод:
# Узел A:
#   - Лист 1
#   - Лист 2
```


#### 11. Мост / Bridge

**Популярность:** 6/10  
**Суть:** Разделяет абстракцию и реализацию так, чтобы они могли изменяться независимо. Вместо наследования использует композицию.

**Пример на Python3:**
```python
from abc import ABC, abstractmethod

class Implementation(ABC):
    @abstractmethod
    def operation_impl(self):
        pass

class ConcreteImplementationA(Implementation):
    def operation_impl(self):
        return "Реализация A"

class ConcreteImplementationB(Implementation):
    def operation_impl(self):
        return "Реализация B"

class Abstraction:
    def __init__(self, implementation: Implementation):
        self._implementation = implementation
    def operation(self):
        return f"Абстракция: {self._implementation.operation_impl()}"

impl_a = ConcreteImplementationA()
abstraction = Abstraction(impl_a)
print(abstraction.operation())  # Вывод: Абстракция: Реализация A
```


#### 12. Приспособленец / Flyweight

**Популярность:** 5/10  
**Суть:** Экономит память, разделяя общее состояние между множеством объектов вместо хранения одинаковых данных в каждом объекте.

**Пример на Python3:**
```python
class Flyweight:
    def __init__(self, shared_state):
        self._shared_state = shared_state
    def operation(self, unique_state):
        return f"Flyweight: Общее ({self._shared_state}), Уникальное ({unique_state})"

class FlyweightFactory:
    _flyweights = {}
    def get_flyweight(self, shared_state):
        if shared_state not in self._flyweights:
            self._flyweights[shared_state] = Flyweight(shared_state)
        return self._flyweights[shared_state]

factory = FlyweightFactory()
f1 = factory.get_flyweight("A")
f2 = factory.get_flyweight("A")
print(f1 is f2)  # Вывод: True
print(f1.operation("1"))  # Вывод: Flyweight: Общее (A), Уникальное (1)
print(f2.operation("2"))  # Вывод: Flyweight: Общее (A), Уникальное (2)
```


### Поведенческие паттерны (Behavioral Patterns)

Решают задачи эффективного и безопасного взаимодействия между объектами программы. Распределяют обязанности между объектами.

---

#### 13. Наблюдатель / Observer

**Популярность:** 9/10  
**Суть:** Определяет зависимость «один ко многим» между объектами таким образом, что при изменении состояния одного объекта все зависящие от него объекты уведомляются и обновляются автоматически.

**Пример на Python3:**
```python
from abc import ABC, abstractmethod

class Observer(ABC):
    @abstractmethod
    def update(self, message): pass

class ConcreteObserverA(Observer):
    def update(self, message):
        print(f"Наблюдатель А: {message}")

class Subject:
    def __init__(self):
        self._observers = []
    def attach(self, observer):
        self._observers.append(observer)
    def notify(self, message):
        for observer in self._observers:
            observer.update(message)

subject = Subject()
obs1 = ConcreteObserverA()
subject.attach(obs1)
subject.notify("Событие 1")  # Вывод: Наблюдатель А: Событие 1
```

#### 14. Стратегия / Strategy

**Популярность:** 9/10  
**Суть:** Определяет семейство алгоритмов, инкапсулирует каждый из них и делает их взаимозаменяемыми. Позволяет изменять алгоритмы независимо от клиентов, которые ими пользуются.

**Пример на Python3:**
```python
from abc import ABC, abstractmethod

class Strategy(ABC):
    @abstractmethod
    def execute(self, data): pass

class ConcreteStrategyA(Strategy):
    def execute(self, data):
        return sorted(data)

class Context:
    def __init__(self, strategy: Strategy):
        self._strategy = strategy
    def do_logic(self, data):
        result = self._strategy.execute(data)
        print(f"Результат: {result}")

data = [3, 1, 4, 1, 5]
context = Context(ConcreteStrategyA())
context.do_logic(data)  # Вывод: Результат: [1, 1, 3, 4, 5]
```


#### 15. Команда / Command

**Популярность:** 8/10  
**Суть:** Инкапсулирует запрос как объект, позволяя параметризовать клиентов с другими запросами, организовывать очередь или журнал запросов, а также поддерживать отмену операций.

**Пример на Python3:**
```python
from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def execute(self): pass

class SimpleCommand(Command):
    def __init__(self, payload):
        self._payload = payload
    def execute(self):
        print(f"Простая команда: {self._payload}")

class Invoker:
    _command = None
    def set_command(self, command: Command):
        self._command = command
    def do_something(self):
        if self._command:
            self._command.execute()

invoker = Invoker()
invoker.set_command(SimpleCommand("Сказать Привет!"))
invoker.do_something()  # Вывод: Простая команда: Сказать Привет!
```


#### 16. Состояние / State

**Популярность:** 7/10  
**Суть:** Позволяет объекту изменять свое поведение при изменении внутреннего состояния. Создается впечатление, что объект изменил свой класс.

**Пример на Python3:**
```python
from abc import ABC, abstractmethod

class State(ABC):
    @abstractmethod
    def handle(self, context): pass

class ConcreteStateA(State):
    def handle(self, context):
        print("Состояние А -> Б")
        context.state = ConcreteStateB()

class Context:
    def __init__(self, state: State):
        self._state = state
    @property
    def state(self):
        return self._state
    @state.setter
    def state(self, state: State):
        self._state = state
    def request(self):
        self._state.handle(self)

context = Context(ConcreteStateA())
context.request()  # Вывод: Состояние А -> Б
```


#### 17. Итератор / Iterator

**Популярность:** 8/10  
**Суть:** Предоставляет способ последовательного доступа к элементам составного объекта без раскрытия его внутреннего представления.

**Пример на Python3:**
```python
class AlphabeticalOrderIterator:
    _position = None
    _reverse = False
    def __init__(self, collection, reverse=False):
        self._collection = collection
        self._reverse = reverse
        self._position = -1 if reverse else 0
    def __next__(self):
        try:
            value = self._collection[self._position]
            self._position += -1 if self._reverse else 1
        except IndexError:
            raise StopIteration()
        return value

class WordsCollection:
    def __init__(self):
        self._collection = []
    def add_item(self, item):
        self._collection.append(item)
    def __iter__(self):
        return AlphabeticalOrderIterator(self._collection)
    def get_reverse_iterator(self):
        return AlphabeticalOrderIterator(self._collection, True)

collection = WordsCollection()
collection.add_item("Первый")
collection.add_item("Второй")
collection.add_item("Третий")
print("Прямой порядок:")
for item in collection:
    print(f"  {item}")
print("Обратный порядок:")
for item in collection.get_reverse_iterator():
    print(f"  {item}")
```


#### 18. Цепочка обязанностей / Chain of Responsibility

**Популярность:** 7/10  
**Суть:** Позволяет передавать запросы последовательно по цепочке обработчиков. Каждый обработчик решает, может ли он обработать запрос, и передаёт дальше.

**Пример на Python3:**
```python
from abc import ABC, abstractmethod

class Handler(ABC):
    _next_handler = None
    def set_next(self, handler):
        self._next_handler = handler
        return handler
    @abstractmethod
    def handle(self, request):
        if self._next_handler:
            return self._next_handler.handle(request)
        return None

class ConcreteHandler1(Handler):
    def handle(self, request):
        if request == "Запрос1":
            return f"Обработчик 1 обработал {request}"
        else:
            return super().handle(request)

class ConcreteHandler2(Handler):
    def handle(self, request):
        if request == "Запрос2":
            return f"Обработчик 2 обработал {request}"
        else:
            return super().handle(request)

class DefaultHandler(Handler):
    def handle(self, request):
        return f"Обработчик по умолчанию: {request}"

h1 = ConcreteHandler1()
h2 = ConcreteHandler2()
default = DefaultHandler()
h1.set_next(h2).set_next(default)

print(h1.handle("Запрос1"))  # Вывод: Обработчик 1 обработал Запрос1
print(h1.handle("Запрос2"))  # Вывод: Обработчик 2 обработал Запрос2
print(h1.handle("Неизвестный"))  # Вывод: Обработчик по умолчанию: Неизвестный
```


#### 19. Посредник / Mediator

**Популярность:** 6/10  
**Суть:** Упрощает взаимодействие множества объектов, инкапсулируя их взаимодействие в отдельном объекте-посреднике.

**Пример на Python3:**
```python
from abc import ABC, abstractmethod

class Mediator(ABC):
    @abstractmethod
    def notify(self, sender, event):
        pass

class ConcreteMediator(Mediator):
    def __init__(self, component1, component2):
        self._component1 = component1
        self._component2 = component2
        self._component1.mediator = self
        self._component2.mediator = self
    def notify(self, sender, event):
        if event == "A":
            print("Посредник реагирует на событие A:")
            self._component2.do_c()
        elif event == "D":
            print("Посредник реагирует на событие D:")
            self._component1.do_b()

class BaseComponent:
    def __init__(self, mediator=None):
        self._mediator = mediator
    @property
    def mediator(self):
        return self._mediator
    @mediator.setter
    def mediator(self, mediator):
        self._mediator = mediator

class Component1(BaseComponent):
    def do_a(self):
        print("Компонент 1 выполняет A.")
        self.mediator.notify(self, "A")
    def do_b(self):
        print("Компонент 1 выполняет B.")

class Component2(BaseComponent):
    def do_c(self):
        print("Компонент 2 выполняет C.")
    def do_d(self):
        print("Компонент 2 выполняет D.")
        self.mediator.notify(self, "D")

c1 = Component1()
c2 = Component2()
mediator = ConcreteMediator(c1, c2)
c1.do_a()
# Вывод:
# Компонент 1 выполняет A.
# Посредник реагирует на событие A:
# Компонент 2 выполняет C.
```


#### 20. Шаблонный метод / Template Method

**Популярность:** 6/10  
**Суть:** Определяет скелет алгоритма в базовом классе, позволяя подклассам переопределять некоторые шаги алгоритма без изменения его общей структуры.

**Пример на Python3:**
```python
from abc import ABC, abstractmethod

class AbstractClass(ABC):
    def template_method(self):
        self.base_operation1()
        self.required_operations1()
        self.base_operation2()
        self.hook1()
        self.required_operations2()
        self.base_operation3()
        self.hook2()
    def base_operation1(self):
        print("Абстрактный класс: Базовая операция 1")
    def base_operation2(self):
        print("Абстрактный класс: Базовая операция 2")
    def base_operation3(self):
        print("Абстрактный класс: Базовая операция 3")
    @abstractmethod
    def required_operations1(self):
        pass
    @abstractmethod
    def required_operations2(self):
        pass
    def hook1(self):
        pass
    def hook2(self):
        pass

class ConcreteClass1(AbstractClass):
    def required_operations1(self):
        print("ConcreteClass1: Реализация required_operations1")
    def required_operations2(self):
        print("ConcreteClass1: Реализация required_operations2")
    def hook2(self):
        print("ConcreteClass1: Переопределён hook2")

class ConcreteClass2(AbstractClass):
    def required_operations1(self):
        print("ConcreteClass2: Реализация required_operations1")
    def required_operations2(self):
        print("ConcreteClass2: Реализация required_operations2")
    def hook1(self):
        print("ConcreteClass2: Переопределён hook1")

print("Клиентский код использует ConcreteClass1:")
concrete1 = ConcreteClass1()
concrete1.template_method()

print("\nКлиентский код использует ConcreteClass2:")
concrete2 = ConcreteClass2()
concrete2.template_method()
```


#### 21. Снимок / Memento

**Популярность:** 5/10  
**Суть:** Позволяет сохранять и восстанавливать предыдущее состояние объекта, не раскрывая деталей его реализации.

**Пример на Python3:**
```python
class Memento:
    def __init__(self, state):
        self._state = state
    def get_state(self):
        return self._state

class Originator:
    _state = None
    def set_state(self, state):
        self._state = state
    def save(self):
        return Memento(self._state)
    def restore(self, memento):
        self._state = memento.get_state()

class Caretaker:
    def __init__(self, originator):
        self._originator = originator
        self._mementos = []
    def backup(self):
        self._mementos.append(self._originator.save())
    def undo(self):
        if not self._mementos:
            return
        memento = self._mementos.pop()
        self._originator.restore(memento)

originator = Originator()
caretaker = Caretaker(originator)

originator.set_state("Состояние 1")
caretaker.backup()
originator.set_state("Состояние 2")
caretaker.backup()
originator.set_state("Состояние 3")
print(f"Текущее состояние: {originator._state}")  # Вывод: Состояние 3
caretaker.undo()
print(f"После отмены: {originator._state}")       # Вывод: Состояние 2
caretaker.undo()
print(f"После второй отмены: {originator._state}") # Вывод: Состояние 1
```


#### 22. Посетитель / Visitor

**Популярность:** 5/10  
**Суть:** Позволяет добавлять новые операции к объектам без изменения их классов путём выноса этих операций в отдельный класс-посетитель.

**Пример на Python3:**
```python
from abc import ABC, abstractmethod

class Component(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass

class ConcreteComponentA(Component):
    def accept(self, visitor):
        visitor.visit_concrete_component_a(self)
    def exclusive_method_of_a(self):
        return "A"

class ConcreteComponentB(Component):
    def accept(self, visitor):
        visitor.visit_concrete_component_b(self)
    def special_method_of_b(self):
        return "B"

class Visitor(ABC):
    @abstractmethod
    def visit_concrete_component_a(self, element):
        pass
    @abstractmethod
    def visit_concrete_component_b(self, element):
        pass

class ConcreteVisitor1(Visitor):
    def visit_concrete_component_a(self, element):
        print(f"Посетитель 1: {element.exclusive_method_of_a()}")
    def visit_concrete_component_b(self, element):
        print(f"Посетитель 1: {element.special_method_of_b()}")

class ConcreteVisitor2(Visitor):
    def visit_concrete_component_a(self, element):
        print(f"Посетитель 2: {element.exclusive_method_of_a()}")
    def visit_concrete_component_b(self, element):
        print(f"Посетитель 2: {element.special_method_of_b()}")

components = [ConcreteComponentA(), ConcreteComponentB()]
visitor1 = ConcreteVisitor1()
visitor2 = ConcreteVisitor2()
for component in components:
    component.accept(visitor1)
for component in components:
    component.accept(visitor2)
# Вывод:
# Посетитель 1: A
# Посетитель 1: B
# Посетитель 2: A
# Посетитель 2: B
```


#### 23. Интерпретатор / Interpreter

**Популярность:** 4/10  
**Суть:** Определяет грамматику языка и интерпретатор для её обработки. Используется для обработки специализированных языков или выражений.

**Пример на Python3:**
```python
from abc import ABC, abstractmethod

class AbstractExpression(ABC):
    @abstractmethod
    def interpret(self, context):
        pass

class TerminalExpression(AbstractExpression):
    def __init__(self, data):
        self._data = data
    def interpret(self, context):
        return self._data in context

class OrExpression(AbstractExpression):
    def __init__(self, expr1, expr2):
        self._expr1 = expr1
        self._expr2 = expr2
    def interpret(self, context):
        return self._expr1.interpret(context) or self._expr2.interpret(context)

class AndExpression(AbstractExpression):
    def __init__(self, expr1, expr2):
        self._expr1 = expr1
        self._expr2 = expr2
    def interpret(self, context):
        return self._expr1.interpret(context) and self._expr2.interpret(context)

expr1 = TerminalExpression("John")
expr2 = TerminalExpression("Robert")
or_expr = OrExpression(expr1, expr2)

print(or_expr.interpret("John"))     # Вывод: True
print(or_expr.interpret("Robert"))   # Вывод: True
print(or_expr.interpret("Mike"))     # Вывод: False
```


---

## ЧАСТЬ 2: ПРИНЦИПЫ ПРОГРАММИРОВАНИЯ

### ЗАКЛЮЧИТЕЛЬНЫЕ РЕКОМЕНДАЦИИ ДЛЯ АГЕНТНЫХ IDE

#### Анализ перед предложением
Всегда анализируйте контекст задачи пользователя. Паттерны и принципы — это средства для решения конкретных проблем (сложность создания, изменения, тестирования), а не цель сами по себе.

#### Приоритет простоты (KISS & YAGNI)
Сначала предлагайте самое простое и прямое решение. Сложные паттерны (Абстрактная фабрика, Посетитель) уместны только при явных признаках необходимости (частая смена семейств объектов, сложные операции над множеством типов).

#### Диагностика через принципы
Используйте SOLID и DRY как диагностические инструменты. Если код пользователя сложно менять — возможно, нарушен SRP или OCP. Если изменения нужно вносить в нескольких местах — нарушен DRY.

#### Адаптация к Python
Учитывайте идиомы Python. Иногда встроенные возможности языка (contextlib, декораторы, dataclasses, __iter__) являются более «питоническим» решением, чем классическая реализация паттерна.

#### Объясняйте выбор
Кратко объясняйте, почему вы предлагаете тот или иной паттерн/принцип для данной ситуации, и какие выгоды он принесет (упростит тестирование, добавление новой функциональности и т.д.).

#### Предупреждайте о сложности
При предложении сложного паттерна отметьте, что он добавляет уровень абстракции, который может быть излишним для простых или стабильных частей приложения.

