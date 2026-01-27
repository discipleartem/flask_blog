# GitHub Actions: Автоматическая синхронизация веток

## Обзор

В проекте настроена автоматическая синхронизация ветки `dev` с `main` через GitHub Actions.

## Файлы конфигурации

### 1. Основной workflow
**Файл**: `.github/workflows/sync-dev-to-main.yml`

```yaml
name: Sync Dev to Main

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  sync-dev:
    runs-on: ubuntu-latest
    if: github.event_name == 'workflow_dispatch' || (github.event_name == 'push' && github.ref == 'refs/heads/main' && !contains(github.event.head_commit.message, '[skip-sync]'))
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        fetch-depth: 0
        
    - name: Wait for checks to complete
      uses: lewagon/wait-on-check-action@v1.3.4
      with:
        ref: ${{ github.ref }}
        check-name: 'Code Quality Checks'
        repo-token: ${{ secrets.GITHUB_TOKEN }}
        wait-interval: 10
        
    - name: Wait for tests to complete
      uses: lewagon/wait-on-check-action@v1.3.4
      with:
        ref: ${{ github.ref }}
        check-name: 'Test Suite'
        repo-token: ${{ secrets.GITHUB_TOKEN }}
        wait-interval: 10
        
    - name: Configure Git
      run: |
        git config --global user.name 'github-actions[bot]'
        git config --global user.email 'github-actions[bot]@users.noreply.github.com'
        
    - name: Sync main to dev
      run: |
        git checkout dev
        git pull origin dev
        git merge origin/main --no-ff -m "Auto-sync: Merge main into dev"
        git push origin dev --force-with-lease
```

## Настройка

### 1. Права доступа GitHub Actions

1. Зайди в репозиторий → **Settings** → **Actions** → **General**
2. Прокрути до секции **"Workflow permissions"**
3. Выбери:
   - ✅ **"Read and write permissions"**
   - ✅ **"Allow GitHub Actions to create and approve pull requests"**
4. Нажми **"Save"**

### 2. Настройка защиты веток

**Ветка `main` (production):**
- Settings → Branches → Add branch protection rule
- ✅ **Require pull request** (для code review)
- ✅ **Require status checks to pass** (CI/CD)
- ✅ **Require branches to be up to date**
- ✅ **Block force pushes** (можно включить)
- ✅ **Restrict deletions** (защита от удаления)

**Ветка `dev` (development):**
- Settings → Branches → Add branch protection rule
- ✅ **Require pull request** (блокирует прямой push)
- ✅ **Require status checks to pass** (quality, test)
- ✅ **Require branches to be up to date**
- ✅ **Code scanning results** (безопасность)
- ✅ **Code quality results** (качество кода)
- ❌ **Block force pushes** (отключить для GitHub Actions)
- ❌ **Restrict updates** (отключить для синхронизации)

**Почему `dev` не блокирует force push:**
- **GitHub Actions** использует `--force-with-lease` для синхронизации
- **Обычные пользователи** не могут force push из-за "Require pull request"
- **Только bot** может форснуть `dev` при синхронизации с `main`

**Repository Rules (если настроены):**
- Settings → Rules → Branches
- Убери правила для `dev` или создай исключение
- GitHub Actions должен иметь права на запись в `dev`

### 3. Проверка токена

`GITHUB_TOKEN` - это встроенный токен GitHub Actions:
- Автоматически предоставляется для каждого workflow
- Имеет права на запись в репозиторий при правильных настройках
- Не требует создания в GitHub Secrets

**Если `GITHUB_TOKEN` не работает:**
1. Создай Personal Access Token:
   - Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token → права `repo`
2. Добавь в Repository → Settings → Secrets → `PAT_TOKEN`
3. Измени workflow: `token: ${{ secrets.PAT_TOKEN }}`

## Как это работает

### Автоматический запуск
- **Триггер**: Каждый push в ветку `main`
- **Действие**: Автоматическое слияние `main` в `dev`
- **Результат**: Ветка `dev` всегда содержит изменения из `main`

### Ручной запуск
- Можно запустить вручную через **Actions** → **Sync Dev to Main** → **Run workflow**

### Процесс синхронизации
1. Checkout репозитория с полным доступом (`fetch-depth: 0`)
2. **Ожидание завершения CI проверок** (Code Quality Checks, Test Suite)
3. Настройка Git конфигурации для bot-пользователя
4. Переключение на ветку `dev`
5. Pull последних изменений `dev`
6. Слияние `origin/main` в `dev` без fast-forward
7. Push обновлённой `dev` в remote

### Условия запуска workflow
- **Автоматически**: При push в `main` (если в коммите нет `[skip-sync]`)
- **Вручную**: Через Actions → Sync Dev to Main → Run workflow
- **Пропуск синхронизации**: Добавь `[skip-sync]` в сообщение коммита

## Альтернативные методы синхронизации

### 1. Git псевдоним (уже настроен)
```bash
git sync-dev
```

Добавлен в `~/.gitconfig`:
```ini
[alias]
    sync-dev = "!f() { git checkout dev && git merge main && git push origin dev; }; f"
```

### 2. Локальный Git hook
**Файл**: `.git/hooks/post-merge`

Автоматически обновляет `dev` после слияния в `main`.

### 3. Ручная синхронизация
```bash
git checkout dev
git merge main
git push origin dev
```

## Решение проблем

### Ошибка: Repository rule violations
**Причина**: Repository Rules блокируют push в `dev`
**Решение**: 
1. **Settings → Rules → Branches** → отключи правила для `dev`
2. **Или создай исключение** для `github-actions[bot]`
3. **Или используй Personal Access Token** с полными правами

**Проблема с CI проверками:**
**Причина**: Синхронизация запускается до завершения проверок
**Решение**: 
- Workflow теперь ждёт завершения всех проверок
- Использует `lewagon/wait-on-check-action` для ожидания
- Синхронизация происходит только после успешных проверок

### Важно: Безопасность force push в `dev`
**Кто может форснуть `dev`:**
- ❌ **Обычные контрибьюторы** - не могут (блокировано "Require pull request")
- ✅ **GitHub Actions** - может (bot с правами для синхронизации)
- ✅ **Admins** - могут (но обычно не делают)

**Защита обеспечивается:**
- **Require pull request** блокирует прямой push
- **Status checks** требуют прохождения CI
- **Только GitHub Actions** может использовать `--force-with-lease`

### Ошибка: Permission denied
**Причина**: Недостаточно прав у GitHub Actions
**Решение**: Проверь настройки Workflow permissions в Settings → Actions

### Ошибка: Merge conflict
**Причина**: Конфликт изменений между `main` и `dev`
**Решение**: 
1. Разреши конфликт локально
2. Push изменения в `dev`
3. Повтори push в `main`

### Ошибка: Token not found
**Причина**: Проблемы с `GITHUB_TOKEN`
**Решение**: Создай Personal Access Token:
1. Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Создай токен с правами `repo`
3. Добавь в Repository → Settings → Secrets → `PAT_TOKEN`
4. Измени в workflow: `token: ${{ secrets.PAT_TOKEN }}`

## Мониторинг

### Проверка статуса
- **Actions** → **Sync Dev to Main** - история запусков
- **Commits** -查看 автоматические коммиты с пометкой "Auto-sync"

### Логи
Каждый запуск workflow сохраняет детальные логи всех шагов.

## Рекомендации по настройке веток

### Оптимальная конфигурация

**Ветка `main` (production):**
- ✅ **Защищённая** - Require pull request
- ✅ **CI/CD обязательные** - Status checks
- ✅ **Code review** - Require approvals
- ✅ **Обновление перед merge** - Require branches to be up to date
- ✅ **Block force pushes** - защита истории
- ✅ **Restrict deletions** - защита от удаления

**Ветка `dev` (development):**
- ✅ **Защищённая** - Require pull request (блокирует прямой push)
- ✅ **CI/CD обязательные** - Status checks (quality, test)
- ✅ **Code scanning** - Security alerts
- ✅ **Code quality** - Quality checks
- ✅ **Обновление перед merge** - Require branches to be up to date
- ❌ **Block force pushes** - отключить (для GitHub Actions)
- ❌ **Restrict updates** - отключить (для синхронизации)

**Feature ветки:**
- Создаются из `dev`
- Сливаются в `dev` через pull request
- Не влияют на `main` напрямую

### Workflow процесса

1. **Разработка**: `feature/new-post` → PR → `dev` (с проверками)
2. **Тестирование**: Автоматические тесты на `dev`
3. **Релиз**: `dev` → PR → `main` (с проверками)
4. **Ожидание CI**: GitHub Actions ждёт завершения проверок на `main`
5. **Синхронизация**: `main` → (авто) → `dev` (только после успешных проверок)

### Новые возможности workflow

- **Ожидание проверок**: Workflow ждёт Code Quality Checks и Test Suite
- **Условный запуск**: Только для `main` с исключениями
- **Ручное управление**: `[skip-sync]` в коммите для пропуска синхронизации
- **Безопасность**: Синхронизация только после успешных CI проверок

## Рекомендации

1. **Используй GitHub Actions** для основной автоматизации
2. **Псевдоним `git sync-dev`** для ручного обновления
3. **Регулярно проверяй** статус синхронизации
4. **Следи за конфликтами** при параллельной работе в ветках
5. **Держи `main` защищённой** - только через PR
6. **Держи `dev` защищённой, но с исключениями** - для GitHub Actions
7. **Проверяй CI статус** перед слиянием PR в `dev`
8. **Следи за логами GitHub Actions** при проблемах синхронизации
9. **Используй `[skip-sync]`** для временного отключения синхронизации
10. **Настрой Repository Rules** правильно - отключи для `dev` или создай исключения

## Структура файлов

```
.github/
├── workflows/
│   ├── ci.yml                 # Основной CI/CD pipeline
│   └── sync-dev-to-main.yml   # Синхронизация веток
└── ...

.git/
└── hooks/
    └── post-merge             # Локальный hook для синхронизации

docs/
└── github-actions-setup.md    # Этот файл документации
```
