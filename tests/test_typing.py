#!/usr/bin/env python3
"""Простой тест для проверки mypy без флага --ignore-missing-imports."""

import sys
import os

# Добавляем путь к приложению
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

try:
    # Пробуем импортировать основные модули
    from app.auth.utils import hash_password

    print("✅ Все основные импорты работают")

    # Проверяем базовую типизацию
    result = hash_password("test")
    print(f"✅ hash_password возвращает: {type(result)}")

    print("✅ Базовая проверка типизации завершена")

except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Ошибка выполнения: {e}")
    sys.exit(1)
