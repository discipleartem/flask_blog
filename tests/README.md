# tests/README.md
# Примеры использования фикстур для разных типов тестов

## Фикстуры

### Unit тесты (CSRF отключен)
```python
def test_unit_functionality(client, auth):
    """Тестирование бизнес-логики без CSRF."""
    # client использует приложение с WTF_CSRF_ENABLED=False
    # auth работает без CSRF токенов
    response = client.post('/auth/login', data={
        'username': 'test_user#1234',
        'password': 'test_pass'
    })
    assert response.status_code == 302
```

### Интеграционные тесты (CSRF включен)
```python
def test_integration_workflow(client_with_csrf, auth_with_csrf):
    """Тестирование полного сценария с CSRF."""
    # client_with_csrf использует приложение с WTF_CSRF_ENABLED=True
    # auth_with_csrf автоматически обрабатывает CSRF токены
    response = auth_with_csrf.login()
    assert response.status_code == 302
```

### Тесты безопасности (CSRF включен, специальная конфигурация)
```python
def test_csrf_protection(security_client, security_auth):
    """Тестирование защиты от CSRF атак."""
    # security_client использует специальную конфигурацию для тестов безопасности
    # CSRF всегда включен и проверяется строго
    response = security_client.post('/auth/register', data={
        'username': 'test_user',
        'password': 'test_pass',
        'csrf_token': 'wrong_token'  # Неправильный токен
    })
    assert response.status_code == 200  # Форма не принята
    assert b'csrf' in response.data.lower() or b'ошибка' in response.data.lower()
```

## Рекомендации

- **Используй `client`** для unit тестов бизнес-логики
- **Используй `client_with_csrf`** для интеграционных тестов пользовательских сценариев  
- **Используй `security_client`** для тестов безопасности и проверки CSRF защиты

## Запуск тестов по категориям

```bash
# Запустить только unit тесты
pytest -m unit

# Запустить только интеграционные тесты  
pytest -m integration

# Запустить только тесты безопасности
pytest -m security
```
