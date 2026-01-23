# Makefile для Flask Blog

.PHONY: help install install-dev test test-cov test-unit test-integration test-security test-all lint format clean run shell

# Переменные
PYTHON = python3
PIP = pip3
PYTEST = pytest
FLASK = flask
APP_MODULE = wsgi:app

# Цвета для вывода
BLUE = \033[36m
GREEN = \033[32m
YELLOW = \033[33m
RED = \033[31m
NC = \033[0m # No Color

stats: ## Показать статистику проекта
	@echo "$(BLUE)Статистика проекта:$(NC)"
	@echo "$(YELLOW)Строк кода:$(NC)"
	@find app -name "*.py" -exec wc -l {} + | tail -1
	@echo "$(YELLOW)Строк в тестах:$(NC)"
	@find tests -name "*.py" -exec wc -l {} + | tail -1
	@echo "$(YELLOW)Всего файлов Python:$(NC)"
	@find . -name "*.py" | wc -l

docs: ## Сгенерировать документацию
	@echo "$(BLUE)Генерация документации...$(NC)"
	@mkdir -p docs/_build
	sphinx-build -b html docs docs/_build
	@echo "$(GREEN)Документация сгенерирована в docs/_build$(NC)"

help: ## Показать эту справку
	@echo "$(BLUE)Flask Blog - Доступные команды:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Установить зависимости
	@echo "$(YELLOW)Установка зависимостей...$(NC)"
	$(PIP) install -e .

install-dev: ## Установить зависимости для разработки
	@echo "$(YELLOW)Установка зависимостей для разработки...$(NC)"
	$(PIP) install -e ".[dev]"

test: ## Запустить все тесты
	@echo "$(BLUE)Запуск всех тестов...$(NC)"
	$(PYTEST)

test-clean: ## Запустить тесты с чистым выводом (только passed/failed)
	@echo "$(BLUE)Запуск тестов (чистый вывод)...$(NC)"
	@.venv/bin/pytest -c pytest-clean.ini --tb=no -q 2>/dev/null | tail -1 | grep -q "passed" && echo "$(GREEN)✅ Все тесты пройдены!$(NC)" || echo "$(RED)❌ Есть проблемы с тестами$(NC)"

test-cov: ## Запустить тесты с покрытием кода
	@echo "$(BLUE)Запуск тестов с покрытием кода...$(NC)"
	$(PYTEST) -v --cov=app --cov-report=term-missing --cov-report=html:htmlcov

test-unit: ## Запустить только unit тесты
	@echo "$(BLUE)Запуск unit тестов...$(NC)"
	$(PYTEST) -v -m "unit"

test-integration: ## Запустить только интеграционные тесты
	@echo "$(BLUE)Запуск интеграционных тестов...$(NC)"
	$(PYTEST) -v -m "integration"

test-all: ## Запустить все типы тестов
	@echo "$(BLUE)Запуск всех типов тестов...$(NC)"
	$(PYTEST) -v -m "unit or integration or security or database"

test-security: ## Запустить тесты безопасности
	@echo "$(BLUE)Запуск тестов безопасности...$(NC)"
	$(PYTEST) -v -m "security"

test-database: ## Запустить тесты базы данных
	@echo "$(BLUE)Запуск тестов базы данных...$(NC)"
	$(PYTEST) -v -m "database"

test-fast: ## Запустить быстрые тесты (без медленных)
	@echo "$(BLUE)Запуск быстрых тестов...$(NC)"
	$(PYTEST) -v -m "not slow"

lint: ## Проверить код с помощью линтеров
	@echo "$(BLUE)Проверка кода...$(NC)"
	@echo "$(YELLOW)Flake8:$(NC)"
	flake8 app tests
	@echo "$(YELLOW)MyPy:$(NC)"
	mypy app --ignore-missing-imports

format: ## Форматировать код
	@echo "$(BLUE)Форматирование кода...$(NC)"
	black app tests
	@echo "$(GREEN)Код отформатирован!$(NC)"

clean: ## Очистить временные файлы
	@echo "$(YELLOW)Очистка временных файлов...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".pytest_cache" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.db" -delete
	find . -type f -name "*.sqlite" -delete
	@echo "$(GREEN)Очистка завершена!$(NC)"

run: ## Запустить приложение в режиме разработки
	@echo "$(BLUE)Запуск Flask приложения...$(NC)"
	FLASK_ENV=development $(FLASK) run --debug

run-prod: ## Запустить приложение в режиме продакшена
	@echo "$(BLUE)Запуск приложения с gunicorn...$(NC)"
	gunicorn $(APP_MODULE)

shell: ## Запустить Flask shell
	@echo "$(BLUE)Запуск Flask shell...$(NC)"
	$(FLASK) shell

init-db: ## Инициализировать базу данных
	@echo "$(BLUE)Инициализация базы данных...$(NC)"
	$(FLASK) init-db

migrate: ## Выполнить миграции базы данных
	@echo "$(BLUE)Выполнение миграций...$(NC)"
	$(FLASK) db upgrade

migrate-make: ## Создать новую миграцию
	@echo "$(BLUE)Создание миграции...$(NC)"
	$(FLASK) db migrate -m "$(MSG)"

check: ## Проверить код и запустить тесты
	@echo "$(BLUE)Полная проверка проекта...$(NC)"
	$(MAKE) lint
	$(MAKE) test-cov
	@echo "$(GREEN)Проверка завершена!$(NC)"

ci: ## Запустить CI pipeline (lint + быстрые тесты)
	@echo "$(BLUE)CI Pipeline...$(NC)"
	$(MAKE) lint
	$(MAKE) test-fast
	@echo "$(GREEN)CI пройден!$(NC)"

dev-setup: ## Настроить окружение для разработки
	@echo "$(BLUE)Настройка окружения для разработки...$(NC)"
	$(MAKE) install-dev
	$(MAKE) init-db
	@echo "$(GREEN)Окружение настроено!$(NC)"

# Команды для работы с Docker (если понадобится)
docker-build: ## Собрать Docker образ
	@echo "$(BLUE)Сборка Docker образа...$(NC)"
	docker build -t flask-blog .

docker-run: ## Запустить Docker контейнер
	@echo "$(BLUE)Запуск Docker контейнера...$(NC)"
	docker run -p 5000:5000 flask-blog

# Полезные команды для разработки
watch: ## Следить за изменениями и перезапускать приложение
	@echo "$(BLUE)Запуск с отслеживанием изменений...$(NC)"
	watchmedo shell-command --patterns="*.py" --recursive --command='make run' .

debug: ## Запустить приложение в режиме отладки
	@echo "$(BLUE)Запуск в режиме отладки...$(NC)"
	FLASK_ENV=development FLASK_DEBUG=1 $(FLASK) run --debug --host=0.0.0.0

# Проверка безопасности
security-check: ## Проверить безопасность зависимостей
	@echo "$(BLUE)Проверка безопасности зависимостей...$(NC)"
	safety check
