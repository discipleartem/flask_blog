"""JWT middleware и декораторы для авторизации.

Применяемые паттерны:
- Decorator — декоратор для защиты маршрутов
- Middleware — проверка токена для каждого запроса
- Strategy — разные стратегии для разных типов запросов

Применяемые принципы:
- Single Responsibility — только авторизация
- Explicit is better than implicit — явные проверки
- Fail fast — ранние проверки и ошибки
"""

from functools import wraps
from typing import Callable, Optional

from flask import current_app, g, redirect, request, session, url_for


def login_required(f: Callable) -> Callable:
    """Декоратор для защиты маршрутов требующих авторизации.
    
    Проверяет наличие валидного JWT токена в cookies и устанавливает
    текущего пользователя в flask.g.current_user
    
    Args:
        f: Декорируемая функция
        
    Returns:
        Обернутая функция с проверкой авторизации
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Проверяем, есть ли токен в cookies
        token = request.cookies.get('auth_token')
        
        if not token:
            # Если это API запрос, возвращаем 401
            if request.path.startswith('/api/'):
                return {'error': 'Требуется авторизация'}, 401
            # Иначе перенаправляем на страницу входа
            return redirect(url_for('auth.login'))
        
        # Проверяем валидность токена
        user = current_app.auth_service.get_user_by_token(token)
        
        if not user:
            # Токен невалиден, удаляем cookie
            response = redirect(url_for('auth.login'))
            response.delete_cookie('auth_token')
            return response
        
        # Устанавливаем текущего пользователя
        g.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function


def admin_required(f: Callable) -> Callable:
    """Декоратор для защиты маршрутов требующих прав администратора.
    
    Проверяет, что текущий пользователь является администратором.
    
    Args:
        f: Декорируемая функция
        
    Returns:
        Обернутая функция с проверкой прав администратора
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Сначала проверяем авторизацию
        token = request.cookies.get('auth_token')
        
        if not token:
            if request.path.startswith('/api/'):
                return {'error': 'Требуется авторизация'}, 401
            return redirect(url_for('auth.login'))
        
        user = current_app.auth_service.get_user_by_token(token)
        
        if not user:
            response = redirect(url_for('auth.login'))
            response.delete_cookie('auth_token')
            return response
        
        # Проверяем права администратора
        if not user.is_admin:
            if request.path.startswith('/api/'):
                return {'error': 'Требуются права администратора'}, 403
            return redirect(url_for('blog.index'))
        
        # Устанавливаем текущего пользователя
        g.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function


def get_current_user() -> Optional[object]:
    """Получает текущего авторизованного пользователя.
    
    Returns:
        Текущий пользователь или None если не авторизован
    """
    return getattr(g, 'current_user', None)


def is_authenticated() -> bool:
    """Проверяет, авторизован ли текущий пользователь.
    
    Returns:
        True если пользователь авторизован
    """
    return get_current_user() is not None


def is_admin() -> bool:
    """Проверяет, является ли текущий пользователь администратором.
    
    Returns:
        True если пользователь является администратором
    """
    user = get_current_user()
    return user is not None and user.is_admin


def load_user_from_token():
    """Middleware для загрузки пользователя из JWT токена.
    
    Вызывается перед каждым запросом для установки текущего пользователя
    на основе JWT токена в cookies.
    """
    # Пропускаем статические файлы и ошибки
    if request.endpoint == 'static' or request.path.startswith('/static/'):
        return
    
    # Пробуем получить токен из cookies
    token = request.cookies.get('auth_token')
    
    if token:
        # Проверяем валидность токена
        user = current_app.auth_service.get_user_by_token(token)
        
        if user:
            # Устанавливаем текущего пользователя
            g.current_user = user
        else:
            # Токен невалиден, удаляем cookie
            if hasattr(request, 'response'):
                request.response.delete_cookie('auth_token')


def set_auth_cookie(response, token: str, remember_me: bool = False):
    """Устанавливает JWT токен в cookies.
    
    Args:
        response: Flask response объект
        token: JWT токен
        remember_me: Запомнить пользователя на 30 дней
    """
    max_age = 30 * 24 * 60 * 60 if remember_me else 24 * 60 * 60  # 30 дней или 24 часа
    
    response.set_cookie(
        'auth_token',
        token,
        max_age=max_age,
        httponly=True,
        samesite='Lax',
        secure=current_app.config.get('SESSION_COOKIE_SECURE', False)
    )


def clear_auth_cookie(response):
    """Удаляет JWT токен из cookies.
    
    Args:
        response: Flask response объект
    """
    response.delete_cookie('auth_token')