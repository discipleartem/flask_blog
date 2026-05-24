"""Blueprint для авторизации и аутентификации.

Применяемые паттерны:
- Controller — обработка HTTP запросов авторизации
- Blueprint — организация маршрутов авторизации
- Form Validation — валидация форм

Применяемые принципы:
- Single Responsibility — только авторизация
- Explicit is better than implicit — явные ответы
- Fail fast — ранние проверки и ошибки
"""

from flask import Blueprint, current_app, redirect, render_template, request, url_for

from ..auth import set_auth_cookie

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация нового пользователя."""
    if request.method == 'GET':
        return render_template('auth/register.html')
    
    # POST запрос
    login = request.form.get('login', '').strip()
    password = request.form.get('password', '')
    password_confirm = request.form.get('password_confirm', '')
    
    # Базовая валидация
    if not login:
        return render_template('auth/register.html', error='Логин обязателен')
    
    if not password:
        return render_template('auth/register.html', error='Пароль обязателен')
    
    if password != password_confirm:
        return render_template('auth/register.html', error='Пароли не совпадают')
    
    # Регистрация пользователя
    success, message, user = current_app.auth_service.register_user(login, password)
    
    if success:
        # Сохраняем полный логин с дискриминатором для автозаполнения браузера
        full_login = f"{user.login}#{user.discriminator}"
        
        # Автоматический вход после регистрации
        if user and user.discriminator:
            token_success, token_message, token = current_app.auth_service.login_user(
                login, password, user.discriminator
            )
        else:
            # Fallback для admin или если дискриминатор не установлен
            token_success, token_message, token = current_app.auth_service.login_user(
                login, password, None
            )
        
        if token_success and token:
            response = redirect(url_for('blog.index'))
            set_auth_cookie(response, token)
            
            # Сохраняем полный логин для отображения
            full_login = f"{user.login}#{user.discriminator}"
            response.set_cookie(
                'last_full_login',
                full_login,
                max_age=30*24*60*60,  # 30 дней
                httponly=False,  # чтобы JavaScript мог получить доступ
                samesite='Lax'
            )
            
            # Сохраняем простой логин для автозаполнения формы
            response.set_cookie(
                'last_login',
                user.login,
                max_age=30*24*60*60,  # 30 дней
                httponly=False,
                samesite='Lax'
            )
            
            return response
        else:
            return render_template('auth/register.html', 
                                 error='Регистрация успешна, но не удалось войти: ' + token_message)
    else:
        return render_template('auth/register.html', error=message)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Вход пользователя."""
    if request.method == 'GET':
        # Проверяем, есть ли сохранённый логин
        last_login = request.cookies.get('last_login')
        login_value = last_login or ''
        
        return render_template('auth/login.html', login=login_value)
    
    # POST запрос
    login_input = request.form.get('login', '').strip()
    password = request.form.get('password', '')
    remember_me = request.form.get('remember_me') == 'on'
    
    # Базовая валидация
    if not login_input:
        return render_template('auth/login.html', error='Логин обязателен')
    
    if not password:
        return render_template('auth/login.html', error='Пароль обязателен')
    
    # Всегда используем полный логин из cookies для авторизации
    last_full_login = request.cookies.get('last_full_login')
    if last_full_login and '#' in last_full_login:
        parts = last_full_login.split('#')
        if len(parts) == 2:
            stored_login = parts[0].strip()
            discriminator = parts[1].strip()
            
            # Проверяем, что логин совпадает с введенным
            if stored_login != login_input:
                # Если логины не совпадают, ищем все аккаунты пользователя
                from ..repositories import UserRepository
                user_repo = UserRepository()
                users = user_repo.find_by_login(login_input)
                
                if not users:
                    return render_template('auth/login.html', 
                                         login=login_input,
                                         error='Пользователь не найден. Пройдите регистрацию.')
                
                # Ищем аккаунт с правильным паролем
                authenticated_users = []
                for user in users:
                    success, message, token = current_app.auth_service.login_user(
                        user.login, password, user.discriminator, remember_me=False
                    )
                    if success and token:
                        authenticated_users.append({
                            'user': user,
                            'token': token
                        })
                
                if not authenticated_users:
                    return render_template('auth/login.html', 
                                         login=login_input,
                                         error='Неверный пароль')
                
                # Если найден только один аккаунт, входим в него
                if len(authenticated_users) == 1:
                    auth_info = authenticated_users[0]
                    response = _complete_login(auth_info['user'], auth_info['token'], remember_me)
                    
                    # Обновляем информацию об аккаунтах
                    _update_user_accounts(response, authenticated_users)
                    return response
                
                # Если аккаунтов несколько, сохраняем информацию и просим выбрать
                # TODO: добавить страницу выбора аккаунтов
                # Временно выбираем первый
                auth_info = authenticated_users[0]
                response = _complete_login(auth_info['user'], auth_info['token'], remember_me)
                
                # Сохраняем информацию обо всех аккаунтах
                _update_user_accounts(response, authenticated_users)
                return response
            
            # Логины совпадают, используем сохраненный аккаунт
            from ..repositories import UserRepository
            user_repo = UserRepository()
            user = user_repo.find_by_login_and_discriminator(stored_login, discriminator)
            
            if not user:
                return render_template('auth/login.html', 
                                     error='Сохранённый аккаунт не найден. Пройдите регистрацию.')
            
            # Пробуем войти
            success, message, token = current_app.auth_service.login_user(
                stored_login, password, discriminator, remember_me
            )
            
            if success and token:
                return _complete_login(user, token, remember_me)
            else:
                return render_template('auth/login.html', 
                                     login=login_input,
                                     error='Неверный пароль')
    
    # Если нет полного логина в cookies, ищем по простому логину
    from ..repositories import UserRepository
    user_repo = UserRepository()
    users = user_repo.find_by_login(login_input)
    
    if not users:
        return render_template('auth/login.html', 
                             login=login_input,
                             error='Пользователь не найден. Пройдите регистрацию.')
    
    if len(users) == 1:
        # Если пользователь один, входим в него и сохраняем полный логин
        user = users[0]
        success, message, token = current_app.auth_service.login_user(
            user.login, password, user.discriminator, remember_me
        )
        
        if success and token:
            response = _complete_login(user, token, remember_me)
            # Сохраняем информацию об аккаунтах
            _update_user_accounts(response, [{'user': user, 'token': token}])
            return response
        else:
            return render_template('auth/login.html', 
                                 login=login_input,
                                 error='Неверный пароль')
    else:
        # Если пользователей несколько, ищем тот что подходит по паролю
        authenticated_users = []
        for user in users:
            success, message, token = current_app.auth_service.login_user(
                user.login, password, user.discriminator, remember_me=False
            )
            if success and token:
                authenticated_users.append({
                    'user': user,
                    'token': token
                })
        
        if not authenticated_users:
            return render_template('auth/login.html', 
                                 login=login_input,
                                 error='Неверный пароль')
        
        # Входим в первый подходящий и сохраняем информацию обо всех
        auth_info = authenticated_users[0]
        response = _complete_login(auth_info['user'], auth_info['token'], remember_me)
        
        # Сохраняем информацию обо всех аккаунтах
        _update_user_accounts(response, authenticated_users)
        return response


def _update_user_accounts(response, authenticated_users):
    """Обновляет информацию об аккаунтах в cookies."""
    accounts_info = []
    for auth_info in authenticated_users:
        full_login = f"{auth_info['user'].login}#{auth_info['user'].discriminator}"
        accounts_info.append({
            'full_login': full_login,
            'user_id': auth_info['user'].id
        })
    
    import json
    response.set_cookie(
        'user_accounts',
        json.dumps(accounts_info),
        max_age=30*24*60*60,  # 30 дней
        httponly=True,  # Безопасно храним в cookies
        samesite='Lax'
    )


def _complete_login(user, token, remember_me: bool):
    """Завершает процесс входа пользователя."""
    response = redirect(url_for('blog.index'))
    set_auth_cookie(response, token, remember_me)
    
    # Сохраняем полный логин для отображения
    full_login = f"{user.login}#{user.discriminator}"
    response.set_cookie(
        'last_full_login',
        full_login,
        max_age=30*24*60*60,  # 30 дней
        httponly=False,  # чтобы JavaScript мог получить доступ
        samesite='Lax'
    )
    
    # Сохраняем простой логин для автозаполнения формы
    response.set_cookie(
        'last_login',
        user.login,
        max_age=30*24*60*60,  # 30 дней
        httponly=False,
        samesite='Lax'
    )
    
    return response


@auth_bp.route('/logout')
def logout():
    """Выход пользователя."""
    response = redirect(url_for('auth.login'))
    from ..auth import clear_auth_cookie
    clear_auth_cookie(response)
    
    # Удаляем все cookies с логинами и аккаунтами
    response.delete_cookie('last_full_login')
    response.delete_cookie('last_login')
    response.delete_cookie('user_accounts')
    
    return response

