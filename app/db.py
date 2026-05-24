"""Слой доступа к данным для SQLite.

Применяемые паттерны:
- Repository (Хранилище) — инкапсулирует логику доступа к данным
- Connection Manager — управление подключениями к БД
- Data Mapper — преобразование строк БД в объекты

Применяемые принципы:
- Single Responsibility — только работа с БД
- Explicit is better than implicit — явные SQL запросы
- Don't Repeat Yourself — хелперы для повторяющихся операций
"""

import os
try:
    import sqlite3
except ImportError:
    import pysqlite3 as sqlite3
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple, Union

import flask
from werkzeug.local import LocalProxy


def get_db_path() -> str:
    """Получает путь к файлу базы данных из конфигурации."""
    database_url = flask.current_app.config.get('DATABASE_URL', 'sqlite:///blog.db')
    
    # Преобразуем sqlite:///path в путь к файлу
    if database_url.startswith('sqlite:///'):
        return database_url[10:]  # Убираем 'sqlite:///'
    elif database_url.startswith('sqlite://'):
        return database_url[9:]   # Убираем 'sqlite://'
    else:
        return database_url


@contextmanager
def get_db():
    """Контекстный менеджер для работы с базой данных.
    
    Yields:
        sqlite3.Connection: Подключение к базе данных с row_factory=dict
        
    Применяемые принципы:
    - Context Manager — автоматическое управление ресурсами
    - Row Factory — возвращаем словари вместо кортежей
    """
    db_path = get_db_path()
    
    # Создаём директорию для БД если она не существует
    os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Возвращаем Row объекты (как словари)
    
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute_query(
    query: str, 
    params: Optional[Tuple[Any, ...]] = None,
    fetch_one: bool = False,
    fetch_all: bool = False
) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
    """Выполняет SQL запрос и возвращает результат.
    
    Args:
        query: SQL запрос с плейсхолдерами ?
        params: Параметры для запроса
        fetch_one: Вернуть одну запись
        fetch_all: Вернуть все записи
        
    Returns:
        Результат запроса в зависимости от флагов
        
    Применяемые принципы:
    - Explicit parameters — явная передача параметров
    - Type safety — строгие типы возвращаемых значений
    """
    with get_db() as conn:
        cursor = conn.execute(query, params or ())
        
        if fetch_one:
            row = cursor.fetchone()
            return dict(row) if row else None
        elif fetch_all:
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        else:
            # Для INSERT/UPDATE/DELETE запросов
            conn.commit()
            return None


def execute_insert(query: str, params: Optional[Tuple[Any, ...]] = None) -> int:
    """Выполняет INSERT запрос и возвращает ID созданной записи.
    
    Args:
        query: INSERT SQL запрос
        params: Параметры для запроса
        
    Returns:
        ID последней вставленной записи
        
    Применяемые принципы:
    - Single Responsibility — только INSERT операции
    - Explicit return type — всегда возвращает int
    """
    with get_db() as conn:
        cursor = conn.execute(query, params or ())
        conn.commit()
        return cursor.lastrowid


def execute_update(query: str, params: Optional[Tuple[Any, ...]] = None) -> int:
    """Выполняет UPDATE/DELETE запрос и возвращает количество изменённых строк.
    
    Args:
        query: UPDATE/DELETE SQL запрос
        params: Параметры для запроса
        
    Returns:
        Количество изменённых строк
        
    Применяемые принципы:
    - Explicit return type — всегда возвращает int
    - Transaction safety — автоматический commit/rollback
    """
    with get_db() as conn:
        cursor = conn.execute(query, params or ())
        conn.commit()
        return cursor.rowcount


def execute_batch(
    query: str, 
    params_list: List[Tuple[Any, ...]]
) -> int:
    """Выполняет batch операцию для множества записей.
    
    Args:
        query: SQL запрос с плейсхолдерами
        params_list: Список параметров для каждого выполнения
        
    Returns:
        Общее количество обработанных строк
        
    Применяемые принципы:
    - Performance — batch операции вместо множества отдельных запросов
    - Atomic operations — всё или ничего
    """
    with get_db() as conn:
        cursor = conn.executemany(query, params_list)
        conn.commit()
        return cursor.rowcount


# Глобальный объект для доступа к БД через LocalProxy
db = LocalProxy(lambda: get_db())


def init_db() -> None:
    """Инициализирует базу данных, создаёт таблицы.
    
    Применяемые принципы:
    - Idempotent operations — можно вызывать многократно
    - Explicit initialization — явное создание структуры БД
    """
    # Эта функция будет вызываться из миграций
    pass
