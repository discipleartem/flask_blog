"""Точка входа в приложение Flask Blog.

Применяемые паттерны:
- Application Runner — точка входа для запуска приложения
- Configuration Selector — выбор конфигурации на основе окружения

Применяемые принципы:
- Explicit is better than implicit — явный запуск приложения
- Simple is better than complex — минимальная точка входа
"""

import os
from typing import Any

from app import create_app
from app.config import config


def main() -> None:
    """Основная функция для запуска приложения."""
    # Определяем конфигурацию на основе переменной окружения
    env = os.getenv('FLASK_ENV', 'development')
    config_class = config.get(env, config['default'])
    
    # Создаём приложение
    app = create_app(config_class)
    
    # Запускаем приложение
    port = app.config.get('PORT', 5000)
    debug = app.config.get('DEBUG', False)
    
    print(f"🚀 Запуск Flask Blog на порту {port} (режим: {env})")
    print(f"📊 База данных: {app.config.get('DATABASE_URL')}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,  # Отключаем debug из-за проблем с ctypes
        use_reloader=False  # Отключаем reloader из-за проблем с ctypes
    )


if __name__ == '__main__':
    main()
