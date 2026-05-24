---
trigger: always_on
---
# ЧИСТАЯ АРХИТЕКТУРА ПО РОБЕРТУ МАРТИНУ

**Версия:** 1.0  
**Источник:** "Чистая архитектура. Искусство разработки программного обеспечения" - Роберт Мартин  
**Применимость:** Все проекты, особенно сложные бизнес-приложения  

---

## 📋 Оглавление

1. [Основные принципы](#1-основные-принципы)
2. [Правила зависимостей](#2-правила-зависимостей)
3. [Структура слоев](#3-структура-слоев)
4. [Практические правила для Python](#4-практические-правила-для-python)
5. [Диагностика нарушений](#5-диагностика-нарушений)
6. [Примеры рефакторинга](#6-примеры-рефакторинга)

---

## 1. ОСНОВНЫЕ ПРИНЦИПЫ

### The Dependency Rule (Правило зависимостей)
```text
Исходный код зависимостей может указывать на внутренние модули,
но внутренние модули не могут указывать на исходный код зависимостей.
```

**Важность:** 10/10 - это фундаментальный принцип чистой архитектуры

### Направление зависимостей
```
Внешние слои → Внутренние слои
UI/Controllers → Use Cases → Entities
Frameworks → Interfaces → Business Rules
```

### Independence of Layers (Независимость слоев)
- **Business Rules** не зависят от UI, базы данных, внешних сервисов
- **Use Cases** не зависят от UI, базы данных, но зависят от Business Rules
- **Interface Adapters** зависят от Use Cases и Business Rules
- **Frameworks & Drivers** зависят от всех внутренних слоев

---

## 2. ПРАВИЛА ЗАВИСИМОСТЕЙ

### ✅ Правильные зависимости
```python
# ✅ Use Case зависит от Entity
from src.models.entities import User
from src.interfaces.user_repository import UserRepository

class CreateUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def execute(self, user_data: dict) -> User:
        user = User.create(user_data)
        return self.user_repo.save(user)

# ✅ Controller зависит от Use Case
from src.use_cases.create_user import CreateUserUseCase

class UserController:
    def __init__(self, create_user: CreateUserUseCase):
        self.create_user = create_user
```

### ❌ Неправильные зависимости
```python
# ❌ Entity зависит от базы данных
class User:
    def save(self):
        db.session.add(self)  # Нарушение!
    
    def send_notification(self):
        EmailService.send(...)  # Нарушение!

# ❌ Use Case зависит от UI
class CreateUserUseCase:
    def execute(self, form_data):  # form_data из UI
        if not form_data.is_valid():  # Зависит от UI
            return ValidationError
```

---

## 3. СТРУКТУРА СЛОЕВ

### Слой Entities (Сущности)
**Назначение:** Бизнес-правила и сущности предприятия
**Зависимости:** Никаких внешних зависимостей

```python
# ✅ Чистая Entity
from dataclasses import dataclass
from typing import List

@dataclass
class Character:
    """Бизнес-сущность персонажа D&D."""
    name: str
    level: int
    hit_points: int
    
    def take_damage(self, damage: int) -> None:
        """Бизнес-правило: получение урона."""
        self.hit_points = max(0, self.hit_points - damage)
        if self.hit_points == 0:
            self._handle_death()
    
    def _handle_death(self) -> None:
        """Внутренняя бизнес-логика."""
        pass
    
    def is_alive(self) -> bool:
        """Бизнес-правило: проверка жизни."""
        return self.hit_points > 0
```

### Слой Use Cases (Сценарии использования)
**Назначение:** Правила приложения и сценарии использования
**Зависимости:** Только от Entities

```python
# ✅ Чистый Use Case
from src.models.entities import Character
from src.interfaces.character_repository import CharacterRepository

class CreateCharacterUseCase:
    """Сценарий создания персонажа."""
    
    def __init__(self, character_repo: CharacterRepository):
        self.character_repo = character_repo
    
    def execute(self, character_data: dict) -> Character:
        """Создать нового персонажа."""
        # Валидация бизнес-правил
        if not self._is_valid_character_data(character_data):
            raise InvalidCharacterDataError()
        
        # Создание сущности
        character = Character.create(character_data)
        
        # Сохранение через интерфейс
        return self.character_repo.save(character)
    
    def _is_valid_character_data(self, data: dict) -> bool:
        """Бизнес-валидация."""
        return len(data.get('name', '')) > 0 and data.get('level', 0) >= 1
```

### Слой Interface Adapters (Адаптеры интерфейсов)
**Назначение:** Преобразование данных между слоями
**Зависимости:** Use Cases и Entities

```python
# ✅ Controller (Interface Adapter)
from src.use_cases.create_character import CreateCharacterUseCase
from src.models.entities import Character

class CharacterController:
    """Адаптер для работы с персонажами."""
    
    def __init__(self, create_character: CreateCharacterUseCase):
        self.create_character = create_character
    
    def create_character(self, request_data: dict) -> dict:
        """Обработать HTTP запрос."""
        try:
            # Преобразование данных
            character_data = self._transform_request_data(request_data)
            
            # Вызов Use Case
            character = self.create_character.execute(character_data)
            
            # Преобразование ответа
            return self._transform_character_to_response(character)
            
        except InvalidCharacterDataError:
            return {"error": "Invalid character data"}
    
    def _transform_request_data(self, request_data: dict) -> dict:
        """Преобразовать данные запроса."""
        return {
            'name': request_data.get('name'),
            'level': int(request_data.get('level', 1))
        }
    
    def _transform_character_to_response(self, character: Character) -> dict:
        """Преобразовать сущность в ответ."""
        return {
            'id': character.id,
            'name': character.name,
            'level': character.level,
            'hit_points': character.hit_points
        }
```

### Слой Frameworks & Drivers
**Назначение:** Внешние интерфейсы (Web, Database, External APIs)
**Зависимости:** Все внутренние слои

```python
# ✅ Repository Implementation (Framework Layer)
from src.interfaces.character_repository import CharacterRepository
from src.models.entities import Character
from sqlalchemy.orm import Session

class SQLAlchemyCharacterRepository(CharacterRepository):
    """Реализация репозитория с SQLAlchemy."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, character: Character) -> Character:
        """Сохранить персонажа в базу данных."""
        db_character = CharacterModel(
            name=character.name,
            level=character.level,
            hit_points=character.hit_points
        )
        self.session.add(db_character)
        self.session.commit()
        
        character.id = db_character.id
        return character
    
    def find_by_id(self, character_id: int) -> Character:
        """Найти персонажа по ID."""
        db_character = self.session.query(CharacterModel).filter(
            CharacterModel.id == character_id
        ).first()
        
        if not db_character:
            return None
        
        return Character(
            id=db_character.id,
            name=db_character.name,
            level=db_character.level,
            hit_points=db_character.hit_points
        )
```

---

## 4. ПРАКТИЧЕСКИЕ ПРАВИЛА ДЛЯ PYTHON

### Правило 1: Импорты только внутрь
```python
# ✅ Правильно - импорты направлены внутрь
# src/use_cases/create_character.py
from src.models.entities import Character          # Внутренний слой
from src.interfaces.repositories import CharacterRepository  # Интерфейс

# ❌ Неправильно - импорты направлены наружу
# src/models/entities/character.py
from src.use_cases.create_character import CreateUserUseCase  # Нарушение!
from src.database.sqlalchemy_models import CharacterModel      # Нарушение!
```

### Правило 2: Интерфейсы для внешних зависимостей
```python
# ✅ Создавайте интерфейсы для всех внешних зависимостей
from abc import ABC, abstractmethod
from typing import List, Optional

class CharacterRepository(ABC):
    """Интерфейс репозитория персонажей."""
    
    @abstractmethod
    def save(self, character: Character) -> Character:
        """Сохранить персонажа."""
        pass
    
    @abstractmethod
    def find_by_id(self, character_id: int) -> Optional[Character]:
        """Найти персонажа по ID."""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Character]:
        """Получить всех персонажей."""
        pass

class EmailService(ABC):
    """Интерфейс email сервиса."""
    
    @abstractmethod
    def send_notification(self, to: str, subject: str, body: str) -> bool:
        """Отправить уведомление."""
        pass
```

### Правило 3: Dependency Inversion
```python
# ✅ Внедрение зависимостей через конструктор
class CharacterService:
    """Сервис персонажей с правильными зависимостями."""
    
    def __init__(self, 
                 character_repo: CharacterRepository,
                 email_service: EmailService,
                 notification_service: NotificationService):
        self.character_repo = character_repo
        self.email_service = email_service
        self.notification_service = notification_service
    
    def create_character(self, data: dict) -> Character:
        """Создать персонажа."""
        character = Character.create(data)
        saved_character = self.character_repo.save(character)
        
        # Уведомления через интерфейсы
        self.email_service.send_notification(
            to=data['email'],
            subject='Character Created',
            body=f'Your character {character.name} is ready!'
        )
        
        return saved_character

# ❌ Жёсткие зависимости
class BadCharacterService:
    def __init__(self):
        self.db = SQLAlchemyDatabase()      # Жёсткая зависимость
        self.email = SMTPEmailService()     # Жёсткая зависимость
        self.cache = RedisCache()           # Жёсткая зависимость
```

### Правило 4: DTO для передачи данных
```python
# ✅ Используйте DTO для передачи данных между слоями
from dataclasses import dataclass
from typing import Optional

@dataclass
class CreateCharacterRequest:
    """DTO для запроса создания персонажа."""
    name: str
    level: int
    character_class: str
    race: str

@dataclass
class CharacterResponse:
    """DTO для ответа с данными персонажа."""
    id: Optional[int]
    name: str
    level: int
    character_class: str
    race: str
    hit_points: int
    created_at: str

# Использование в Use Case
class CreateCharacterUseCase:
    def execute(self, request: CreateCharacterRequest) -> CharacterResponse:
        character = Character.create_from_request(request)
        saved = self.character_repo.save(character)
        return CharacterResponse.from_entity(saved)
```

---

## 5. ДИАГНОСТИКА НАРУШЕНИЙ

### 🔍 Проверочные вопросы

#### Уровень Entity
- [ ] Есть ли у сущности зависимости от фреймворков?
- [ ] Знает ли сущность о базе данных?
- [ ] Есть ли у сущности зависимости от UI?
- [ ] Содержит ли сущность только бизнес-логику?

#### Уровень Use Case
- [ ] Есть ли у Use Case зависимости от UI?
- [ ] Есть ли у Use Case прямые зависимости от базы данных?
- [ ] Зависит ли Use Case только от Entities?
- [ ] Описывает ли Use Case конкретный сценарий использования?

#### Уровень Interface Adapter
- [ ] Преобразует ли адаптер данные между форматами?
- [ ] Есть ли у адаптера зависимости от Use Cases?
- [ ] Изолирует ли адаптер фреймворки от бизнес-логики?

#### Уровень Framework
- [ ] Реализует ли слой конкретные технологии?
- [ ] Есть ли у слоя зависимости от всех внутренних слоев?
- [ ] Можно ли легко заменить этот слой?

### 🚨 Красные флаги

```python
# 🚨 Флаг 1: Entity знает о внешнем мире
class User:
    def save_to_database(self):
        db.session.add(self)  # BAD!
    
    def send_email_notification(self):
        EmailService.send(...)  # BAD!

# 🚨 Флаг 2: Use Case зависит от фреймворков
class CreateUserUseCase:
    def execute(self, flask_request):  # BAD!
        user_data = flask_request.json  # BAD!
        return jsonify({"status": "ok"})  # BAD!

# 🚨 Флаг 3: Controller содержит бизнес-логику
class UserController:
    def create_user(self, data):
        # Бизнес-логика в контроллере - BAD!
        if data['age'] < 18:
            raise ValueError("Too young")
        if len(data['name']) < 3:
            raise ValueError("Name too short")
        
        user = User(data)
        return self.user_repo.save(user)

# 🚨 Флаг 4: Жёсткие зависимости
class UserService:
    def __init__(self):
        self.db = PostgreSQLDatabase()  # BAD!
        self.cache = RedisClient()      # BAD!
```

---

## 6. ПРИМЕРЫ РЕФАКТОРИНГА

### Пример 1: Извлечение бизнес-логики из Controller
```python
# ❌ До рефакторинга
class CharacterController:
    def create_character(self, request):
        data = request.json
        
        # Бизнес-логика в контроллере
        if not data.get('name'):
            return {'error': 'Name required'}, 400
        if data.get('level', 1) < 1:
            return {'error': 'Invalid level'}, 400
        if data.get('level', 1) > 20:
            return {'error': 'Level too high'}, 400
        
        character = Character(
            name=data['name'],
            level=data['level']
        )
        
        db.session.add(character)
        db.session.commit()
        
        return {'id': character.id}, 201

# ✅ После рефакторинга
class CharacterController:
    def __init__(self, create_character_use_case):
        self.create_character_use_case = create_character_use_case
    
    def create_character(self, request):
        try:
            request_dto = CreateCharacterRequest.from_request(request)
            response = self.create_character_use_case.execute(request_dto)
            return response.to_dict(), 201
        except ValidationError as e:
            return {'error': str(e)}, 400

class CreateCharacterUseCase:
    def execute(self, request: CreateCharacterRequest) -> CharacterResponse:
        # Бизнес-логика в Use Case
        request.validate()
        
        character = Character.create_from_request(request)
        saved_character = self.character_repo.save(character)
        
        return CharacterResponse.from_entity(saved_character)
```

### Пример 2: Изоляция зависимостей базы данных
```python
# ❌ До рефакторинга
class Character:
    def __init__(self, name, level):
        self.name = name
        self.level = level
    
    def save(self):
        # Прямая зависимость от базы данных
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def find_by_name(cls, name):
        # Прямая зависимость от базы данных
        return db.session.query(cls).filter(cls.name == name).first()

# ✅ После рефакторинга
class Character:
    def __init__(self, name, level):
        self.name = name
        self.level = level
    
    # Никаких методов работы с базой данных!

class CharacterRepository:
    def save(self, character: Character) -> Character:
        db_character = CharacterModel(
            name=character.name,
            level=character.level
        )
        db.session.add(db_character)
        db.session.commit()
        
        character.id = db_character.id
        return character
    
    def find_by_name(self, name: str) -> Optional[Character]:
        db_character = db.session.query(CharacterModel).filter(
            CharacterModel.name == name
        ).first()
        
        if not db_character:
            return None
        
        return Character(
            id=db_character.id,
            name=db_character.name,
            level=db_character.level
        )
```

---

## 📋 CHECKLIST ДЛЯ ЧИСТОЙ АРХИТЕКТУРЫ

### Перед написанием кода
- [ ] Определить бизнес-правила (Entities)
- [ ] Определить сценарии использования (Use Cases)
- [ ] Создать интерфейсы для внешних зависимостей
- [ ] Спланировать структуру слоев

### Во время написания кода
- [ ] Проверить направление зависимостей
- [ ] Убедиться в отсутствии циклических зависимостей
- [ ] Использовать DTO для передачи данных
- [ ] Применять Dependency Injection

### После написания кода
- [ ] Проверить возможность тестирования каждого слоя
- [ ] Убедиться в возможности замены фреймворков
- [ ] Проверить изоляцию бизнес-логики
- [ ] Провести ревью архитектуры

---

## 💡 ПРАКТИЧЕСКИЕ СОВЕТЫ

1. **Начинайте с Entities** - определите основные бизнес-сущности и правила
2. **Создавайте Use Cases** - опишите сценарии использования системы
3. **Определяйте интерфейсы** - создайте абстракции для внешних зависимостей
4. **Реализуйте адаптеры** - создайте преобразователи данных
5. **Добавляйте фреймворки** - внедрите конкретные технологии последними

### Преимущества чистой архитектуры
- **Тестируемость:** Каждый слой можно тестировать изолированно
- **Независимость от фреймворков:** Легко менять технологии
- **Поддерживаемость:** Чёткое разделение ответственности
- **Масштабируемость:** Легко добавлять новую функциональность

---

**Это правило служит руководством для создания поддерживаемых, тестируемых и масштабируемых приложений following принципам чистой архитектуры Роберта Мартина.**
