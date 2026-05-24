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
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import check_password_hash

from ..auth import set_auth_cookie
from ..services.login_attempt_service import LoginAttemptService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
limiter = Limiter(key_func=get_remote_address)
login_attempt_service = LoginAttemptService()


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
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
        # Используем ID пользователя вместо логина и пароля для точной идентификации
        token_success, token_message, token = current_app.auth_service.login_user_by_id(
            user.id, remember_me=False
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
@limiter.limit("10 per minute")
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
    
    # Проверка защиты от bruteforce
    ip_address = request.remote_addr or 'unknown'
    
    # Сначала проверяем, не превысит ли текущая попытка лимит
    if login_attempt_service.will_exceed_max_attempts(ip_address, login_input):
        return render_template('auth/login.html', 
                             login=login_input,
                             error=f"Слишком много неудачных попыток. Попробуйте позже.")
    
    # Проверяем блокировку аккаунта (если известен user_id)
    # Это будет проверено позже после поиска пользователя
    
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
                # Записываем успешную попытку входа
                login_attempt_service.record_login_attempt(ip_address, login_input, True)
                
                return _complete_login(user, token, remember_me)
            else:
                # Записываем неудачную попытку входа
                login_attempt_service.record_login_attempt(ip_address, login_input, False)
                
                return render_template('auth/login.html', 
                                     login=login_input,
                                     error='Неверный пароль')
    
    # Проверяем cookies на наличие сохраненных аккаунтов
    user_accounts_cookie = request.cookies.get('user_accounts')
    
    if user_accounts_cookie:
        # Если есть сохраненные аккаунты в cookies, проверяем их
        import json
        try:
            saved_accounts = json.loads(user_accounts_cookie)
            
            # Фильтруем аккаунты с тем же логином
            matching_accounts = [acc for acc in saved_accounts if acc['full_login'].startswith(login_input + '#')]
            
            if len(matching_accounts) > 1:
                # Если несколько аккаунтов с тем же логином, показываем страницу выбора из cookies
                from flask import session
                session['available_accounts'] = matching_accounts
                session['login_input'] = login_input
                session['remember_me'] = remember_me
                session['password'] = password  # Сохраняем пароль для проверки
                
                return redirect(url_for('auth.select_account'))
            
            elif len(matching_accounts) == 1:
                # Если один аккаунт, пробуем войти в него
                account = matching_accounts[0]
                from ..repositories import UserRepository
                user_repo = UserRepository()
                user = user_repo.find_by_id(account['user_id'])
                
                if user and check_password_hash(user.password_hash, password):
                    # Пароль совпадает, входим
                    token_success, token_message, token = current_app.auth_service.login_user_by_id(
                        user.id, remember_me
                    )
                    
                    if token_success and token:
                        # Записываем успешную попытку входа
                        login_attempt_service.record_login_attempt(ip_address, login_input, True)
                        
                        response = _complete_login(user, token, remember_me)
                        # Обновляем cookies с аккаунтами
                        _update_user_accounts_from_session(response, saved_accounts)
                        return response
                    else:
                        # Записываем неудачную попытку входа
                        login_attempt_service.record_login_attempt(ip_address, login_input, False)
                        
                        return render_template('auth/login.html', 
                                             login=login_input,
                                             error='Неверный пароль')
        except (json.JSONDecodeError, KeyError):
            # Если cookies повреждены, игнорируем их и ищем в базе данных
            pass
    
    # Если нет подходящих аккаунтов в cookies или cookies отсутствуют, ищем в базе данных
    from ..repositories import UserRepository
    user_repo = UserRepository()
    users = user_repo.find_by_login(login_input)
    
    if not users:
        # Записываем неудачную попытку входа (пользователь не найден)
        login_attempt_service.record_login_attempt(ip_address, login_input, False)
        
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
            # Записываем успешную попытку входа
            login_attempt_service.record_login_attempt(ip_address, login_input, True)
            
            response = _complete_login(user, token, remember_me)
            # Сохраняем информацию об аккаунтах
            _update_user_accounts(response, [{'user': user, 'token': token}])
            return response
        else:
            # Записываем неудачную попытку входа
            login_attempt_service.record_login_attempt(ip_address, login_input, False)
            
            # Проверяем, нужно ли заблокировать аккаунт
            failed_attempts = login_attempt_service.get_failed_attempts_count(ip_address, login_input)
            if failed_attempts >= login_attempt_service.max_attempts:
                login_attempt_service.lock_account(user.id)
            
            return render_template('auth/login.html', 
                                 login=login_input,
                                 error='Неверный пароль')
    else:
        # Если пользователей несколько, проверяем пароль для каждого
        authenticated_users = []
        for user in users:
            if check_password_hash(user.password_hash, password):
                # Пароль подходит, добавляем в список
                authenticated_users.append({
                    'user': user,
                    'token': None  # Токен будет сгенерирован позже
                })
        
        if not authenticated_users:
            # Записываем неудачную попытку входа (пароль неверный)
            login_attempt_service.record_login_attempt(ip_address, login_input, False)
            
            return render_template('auth/login.html', 
                                 login=login_input,
                                 error='Неверный пароль')
        
        # Если найдено несколько аккаунтов, показываем страницу выбора
        if len(authenticated_users) > 1:
            # Сохраняем информацию об аккаунтах в session для страницы выбора
            from flask import session
            accounts_info = []
            for auth_info in authenticated_users:
                accounts_info.append({
                    'user_id': auth_info['user'].id,
                    'full_login': f"{auth_info['user'].login}#{auth_info['user'].discriminator}"
                })
            session['available_accounts'] = accounts_info
            session['login_input'] = login_input
            session['remember_me'] = remember_me
            session['password'] = password  # Сохраняем пароль для проверки
            
            return redirect(url_for('auth.select_account'))
        
        # Если аккаунт только один, входим в него
        auth_info = authenticated_users[0]
        token_success, token_message, token = current_app.auth_service.login_user_by_id(
            auth_info['user'].id, remember_me
        )
        
        if token_success and token:
            # Записываем успешную попытку входа
            login_attempt_service.record_login_attempt(ip_address, login_input, True)
            
            response = _complete_login(auth_info['user'], token, remember_me)
            # Сохраняем информацию об аккаунтах
            _update_user_accounts(response, [{'user': auth_info['user'], 'token': token}])
            return response
        else:
            # Записываем неудачную попытку входа
            login_attempt_service.record_login_attempt(ip_address, login_input, False)
            
            return render_template('auth/login.html', 
                                 login=login_input,
                                 error='Ошибка при входе')


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


def _update_user_accounts_from_session(response, accounts_info):
    """Обновляет информацию об аккаунтах в cookies на основе данных из session."""
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


@auth_bp.route('/select-account', methods=['GET', 'POST'])
def select_account():
    """Страница выбора аккаунта при наличии нескольких с одинаковым логином."""
    from flask import session
    
    # GET запрос - показываем страницу выбора
    if request.method == 'GET':
        accounts = session.get('available_accounts', [])
        login_input = session.get('login_input', '')
        
        if not accounts:
            return redirect(url_for('auth.login'))
        
        return render_template('auth/select_account.html', 
                             accounts=accounts, 
                             login=login_input)
    
    # POST запрос - обрабатываем выбор аккаунта
    user_id = request.form.get('user_id')
    
    if not user_id:
        return render_template('auth/select_account.html', 
                             accounts=session.get('available_accounts', []),
                             login=session.get('login_input', ''),
                             error='Не выбран аккаунт')
    
    # Находим выбранного пользователя
    from ..repositories import UserRepository
    user_repo = UserRepository()
    user = user_repo.find_by_id(int(user_id))
    
    if not user:
        return render_template('auth/select_account.html', 
                             accounts=session.get('available_accounts', []),
                             login=session.get('login_input', ''),
                             error='Аккаунт не найден')
    
    # Проверяем пароль
    password = session.get('password', '')
    if not password or not check_password_hash(user.password_hash, password):
        return render_template('auth/select_account.html', 
                             accounts=session.get('available_accounts', []),
                             login=session.get('login_input', ''),
                             error='Неверный пароль')
    
    # Генерируем токен для выбранного пользователя
    remember_me = session.get('remember_me', False)
    token_success, token_message, token = current_app.auth_service.login_user_by_id(
        user.id, remember_me
    )
    
    if not token_success or not token:
        return render_template('auth/select_account.html', 
                             accounts=session.get('available_accounts', []),
                             login=session.get('login_input', ''),
                             error=token_message)
    
    # Завершаем вход
    response = _complete_login(user, token, remember_me)
    
    # Сохраняем информацию об аккаунтах из cookies
    user_accounts_cookie = request.cookies.get('user_accounts')
    if user_accounts_cookie:
        import json
        try:
            saved_accounts = json.loads(user_accounts_cookie)
            _update_user_accounts_from_session(response, saved_accounts)
        except (json.JSONDecodeError, KeyError):
            pass
    
    # Очищаем session
    session.pop('available_accounts', None)
    session.pop('login_input', None)
    session.pop('remember_me', None)
    session.pop('password', None)
    
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

