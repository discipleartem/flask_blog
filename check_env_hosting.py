#!/usr/bin/env python3
"""Скрипт для проверки загрузки .env на хостинге."""

import os
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.insert(0, "/home/discipleartem/flask_blog")

from dotenv import load_dotenv


def main():
    """Проверяет загрузку переменных окружения."""

    # Проверяем путь к .env файлу
    project_root = Path("/home/discipleartem/flask_blog")
    env_path = project_root / ".env"

    print(f"Корень проекта: {project_root}")
    print(f"Путь к .env: {env_path}")
    print(f".env файл существует: {env_path.exists()}")

    if env_path.exists():
        print(f"Размер .env файла: {env_path.stat().st_size} байт")
        with open(env_path, "r") as f:
            content = f.read()
            print(f"Содержимое .env:\n{content}")

    # Загружаем переменные
    load_dotenv(env_path)

    print(f"\nПосле загрузки:")
    print(f"ADMIN_PASSWORD: {os.environ.get('ADMIN_PASSWORD')}")
    print(
        f"SECRET_KEY: {'установлен' if os.environ.get('SECRET_KEY') else 'не установлен'}"
    )

    # Проверяем через приложение
    from app import create_app

    app = create_app()
    print(f"\nЧерез приложение:")
    print(f"ADMIN_PASSWORD: {app.config.get('ADMIN_PASSWORD')}")


if __name__ == "__main__":
    main()
