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
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      with:
        token: ${{ secrets.GITHUB_TOKEN }}
        fetch-depth: 0
        
    - name: Configure Git
      run: |
        git config --global user.name 'github-actions[bot]'
        git config --global user.email 'github-actions[bot]@users.noreply.github.com'
        
    - name: Sync main to dev
      run: |
        git checkout dev
        git pull origin dev
        git merge origin/main --no-ff -m "Auto-sync: Merge main into dev"
        git push origin dev
```

## Настройка

### 1. Права доступа GitHub Actions

1. Зайди в репозиторий → **Settings** → **Actions** → **General**
2. Прокрути до секции **"Workflow permissions"**
3. Выбери:
   - ✅ **"Read and write permissions"**
   - ✅ **"Allow GitHub Actions to create and approve pull requests"**
4. Нажми **"Save"**

### 2. Проверка токена

`GITHUB_TOKEN` - это встроенный токен GitHub Actions:
- Автоматически предоставляется для каждого workflow
- Имеет права на запись в репозиторий при правильных настройках
- Не требует создания в GitHub Secrets

## Как это работает

### Автоматический запуск
- **Триггер**: Каждый push в ветку `main`
- **Действие**: Автоматическое слияние `main` в `dev`
- **Результат**: Ветка `dev` всегда содержит изменения из `main`

### Ручной запуск
- Можно запустить вручную через **Actions** → **Sync Dev to Main** → **Run workflow**

### Процесс синхронизации
1. Checkout репозитория с полным доступом (`fetch-depth: 0`)
2. Настройка Git конфигурации для bot-пользователя
3. Переключение на ветку `dev`
4. Pull последних изменений `dev`
5. Слияние `origin/main` в `dev` без fast-forward
6. Push обновлённой `dev` в remote

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
1. Settings → Developer settings → Personal access tokens
2. Создай токен с правами `repo`
3. Добавь в Repository → Settings → Secrets → PAT_TOKEN
4. Измени в workflow: `token: ${{ secrets.PAT_TOKEN }}`

## Мониторинг

### Проверка статуса
- **Actions** → **Sync Dev to Main** - история запусков
- **Commits** -查看 автоматические коммиты с пометкой "Auto-sync"

### Логи
Каждый запуск workflow сохраняет детальные логи всех шагов.

## Рекомендации

1. **Используй GitHub Actions** для основной автоматизации
2. **Псевдоним `git sync-dev`** для ручного обновления
3. **Регулярно проверяй** статус синхронизации
4. **Следи за конфликтами** при параллельной работе в ветках

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
