# Правила Cursor (Flask Blog)

Все правила агента — только в [`.cursor/rules/`](rules/).

## Карта правил

| Файл | Scope | Содержание |
|------|-------|------------|
| `00-global.mdc` | always | META, язык, workflow, индекс |
| `01-operations.mdc` | always | `.venv`, Git, секреты |
| `python.mdc` | `**/*.py` | Python 3.12, менторский режим |
| `pep8.mdc` | `**/*.py` | стиль PEP 8 |
| `programming-principles.mdc` | `**/*.py` | KISS, DRY, SOLID, YAGNI |
| `zen-python.mdc` | `**/*.py` | дзен Python |
| `flask.mdc` | `app/**` | Flask 3, слои, чеклист |
| `patterns.mdc` | `app/**` | паттерны проекта |

## Принцип

- **2** правила `alwaysApply` — глобальные и операции
- Остальные — по `globs`, когда открыт нужный код
- Сначала простое → паттерны только если упрощают

## IDE

[`.vscode/settings.json`](../.vscode/settings.json) — интерпретатор `.venv`, pytest, Flask.

## Документация проекта

- [docs/LAYERS.md](../docs/LAYERS.md)
- [AGENTS.md](../AGENTS.md)
