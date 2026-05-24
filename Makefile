.PHONY: help install-dev test test-cov code-quality migrate migrate-up seed db-reset clean

help: ## Показать доступные команды
	@echo ""
	@echo "📦 Установка и тестирование:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && ($$1 ~ /install-dev|test|test-cov/) {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "🔍 Качество кода:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && ($$1 ~ /code-quality/) {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "🗄️ База данных:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && ($$1 ~ /migrate|seed|db-reset/) {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "🧹 Утилиты:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && ($$1 ~ /clean/) && ($$1 !~ /format-check/) {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""

# --- Установка и тестирование ---
install-dev: ## Установить зависимости для разработки
	@. .venv/bin/activate && pip install --upgrade pip && pip install -e ".[dev]"

test: ## Запустить тесты
	@. .venv/bin/activate && pytest -v

test-cov: ## Запустить тесты с покрытием
	@. .venv/bin/activate && pytest --cov=app --cov-report=html --cov-report=term-missing

# --- Качество кода ---
code-quality: ## Проверить и форматировать код (ruff, black, mypy)
	@. .venv/bin/activate && ruff check .
	@. .venv/bin/activate && black .
	@. .venv/bin/activate && ruff format .
	@. .venv/bin/activate && mypy .

# --- База данных ---
migrate: ## Применить миграции базы данных
	@. .venv/bin/activate && flask migrate

migrate-up: ## Обновить схему базы данных
	@. .venv/bin/activate && flask migrate-upgrade

seed: ## Наполнить базу данных тестовыми данными
	@. .venv/bin/activate && flask seed

db-reset: ## Полностью сбросить и пересоздать базу данных
	@. .venv/bin/activate && flask db-reset

# --- Утилиты ---
clean: ## Очистить временные файлы
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type f -name ".coverage" -delete
	@find . -type d -name "htmlcov" -exec rm -rf {} +
	@find . -type d -name ".ruff_cache" -exec rm -rf {} +

