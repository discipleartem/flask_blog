# Flask 3.0.0 Техническая спецификация API

## Техническая документация API

### Объект приложения Flask

#### Основные параметры инициализации

```python
app = Flask(
    import_name,              # Имя модуля/пакета приложения
    static_url_path=None,     # URL путь для статических файлов
    static_folder='static',   # Папка со статическими файлами
    static_host=None,         # Хост для статических файлов
    host_matching=False,      # Включить сопоставление хостов
    subdomain_matching=False, # Включить сопоставление поддоменов
    template_folder='templates', # Папка с шаблонами
    instance_path=None,       # Путь к папке instance
    instance_relative_config=False # Конфигурация относительно instance
)
```

#### Основные методы приложения

**Маршрутизация:**
```python
@app.route('/path', methods=['GET', 'POST'])
def view_function():
    return "Response"

# Динамические маршруты
@app.route('/user/<username>')
@app.route('/post/<int:post_id>')
@app.route('/path/<uuid:identifier>')
```

**Управление конфигурацией:**
```python
app.config['DEBUG'] = True
app.config.from_object('config')
app.config.from_pyfile('config.py')
app.config.from_envvar('FLASK_CONFIG')
```

**Обработка ошибок:**
```python
@app.errorhandler(404)
def not_found(error):
    return "Page not found", 404

@app.errorhandler(Exception)
def handle_exception(e):
    return "Internal error", 500
```

**Хуки (Hooks):**
```python
@app.before_request
def before_request():
    # Выполняется перед каждым запросом
    pass

@app.after_request
def after_request(response):
    # Выполняется после каждого запроса
    return response

@app.teardown_request
def teardown_request(exception):
    # Выполняется после обработки запроса
    pass
```

### Объект запроса (Request)

#### Основные атрибуты

```python
from flask import request

# Метод HTTP
request.method  # 'GET', 'POST', 'PUT', 'DELETE'

# URL и параметры
request.url           # Полный URL
request.base_url      # URL без query параметров
request.path          # Путь без домена
request.query_string  # Query строка
request.args          # Dict с GET параметрами

# Данные формы
request.form          # Dict с POST данными формы
request.files         # Dict с загруженными файлами

# Заголовки
request.headers       # Dict с заголовками
request.user_agent    # User-Agent строка
request.remote_addr   # IP адрес клиента

# Cookies
request.cookies       # Dict с cookies

# JSON данные
request.get_json()    # Парсит JSON из тела запроса
request.is_json       # Проверяет, является ли запрос JSON
```

#### Методы работы с данными

```python
# Получение JSON данных
data = request.get_json(force=True)  # Принудительно парсить JSON

# Работа с файлами
file = request.files['file']
file.save('/path/to/save')

# Проверка типа контента
if request.is_json:
    data = request.get_json()
elif request.form:
    data = request.form.to_dict()
```

### Объект ответа (Response)

#### Создание ответов

```python
from flask import Response, jsonify, make_response

# Простой ответ
return "Hello World"

# Ответ с кодом состояния
return "Not Found", 404

# Ответ с заголовками
return Response("Hello", headers={'X-Custom': 'Value'})

# JSON ответ
return jsonify({'key': 'value'})

# Создание сложного ответа
response = make_response(render_template('index.html'))
response.headers['X-Custom'] = 'Value'
response.set_cookie('name', 'value')
```

#### Методы объекта Response

```python
response = make_response()

# Установка заголовков
response.headers['Content-Type'] = 'application/json'
response.set_cookie('name', 'value', max_age=3600)

# Кэширование
response.cache_control.max_age = 3600
response.etag = 'unique-identifier'

# CORS заголовки
response.headers['Access-Control-Allow-Origin'] = '*'
```

### Конфигурация Flask

#### Встроенные параметры конфигурации

```python
# Основные настройки
DEBUG = False                    # Режим отладки
TESTING = False                  # Режим тестирования
SECRET_KEY = None                # Секретный ключ для сессий

# Настройки сервера
SERVER_NAME = None               # Имя сервера и порт
APPLICATION_ROOT = '/'           # Корень приложения
PREFERRED_URL_SCHEME = 'http'    # Предпочтительная схема URL

# Настройки сессий
SESSION_COOKIE_NAME = 'session' # Имя cookie сессии
SESSION_COOKIE_DOMAIN = None    # Домен для cookie
SESSION_COOKIE_PATH = None      # Путь для cookie
SESSION_COOKIE_HTTPONLY = True  # HTTP-only cookie
SESSION_COOKIE_SECURE = False   # HTTPS-only cookie
SESSION_COOKIE_SAMESITE = 'Lax' # SameSite атрибут

# Безопасность
PERMANENT_SESSION_LIFETIME = timedelta(days=31) # Время жизни сессии
SEND_FILE_MAX_AGE_DEFAULT = 43200              # Время кэширования файлов

# Ограничения
MAX_CONTENT_LENGTH = None          # Максимальный размер запроса
MAX_FORM_MEMORY_SIZE = 500_000     # Максимальный размер формы в памяти
```

#### Управление конфигурацией

```python
# Способы загрузки конфигурации
app.config.from_object('config.Config')        # Из объекта
app.config.from_pyfile('config.py')             # Из файла
app.config.from_envvar('FLASK_SETTINGS')        # из переменной окружения
app.config.from_mapping({'DEBUG': True})         # из словаря

# Доступ к конфигурации
debug_mode = app.config.get('DEBUG', False)
secret = app.config['SECRET_KEY']
```

### Контекст приложения и запроса

#### Application Context

```python
from flask import current_app, g

with app.app_context():
    # current_app - текущее приложение
    # g - глобальный объект для запроса
    g.user = get_current_user()
    current_app.logger.info('Operation completed')
```

#### Request Context

```python
from flask import request, session

with app.test_request_context():
    # request - текущий запрос
    # session - сессия пользователя
    session['user_id'] = 123
    user_agent = request.headers.get('User-Agent')
```

### Работа с шаблонами

#### Рендеринг шаблонов

```python
from flask import render_template, render_template_string

# Рендеринг файла шаблона
return render_template('index.html', name='John', items=[1,2,3])

# Рендеринг строки шаблона
template = "Hello {{ name }}!"
return render_template_string(template, name='John')

# Рендеринг с контекстом
return render_template('admin/dashboard.html', 
                      user=current_user,
                      posts=posts,
                      pagination=pagination)
```

#### Фильтры и глобальные функции

```python
@app.template_filter('reverse')
def reverse_filter(s):
    return s[::-1]

@app.template_global()
def get_config(key):
    return current_app.config.get(key)

# В шаблоне:
# {{ "hello"|reverse }}  # "olleh"
# {{ get_config('DEBUG') }}
```

### Работа с сессиями

```python
from flask import session

# Установка значений
session['username'] = 'john'
session['user_id'] = 123

# Получение значений
username = session.get('username')
user_id = session.get('user_id')

# Удаление значений
session.pop('username', None)

# Очистка сессии
session.clear()

# Постоянная сессия
session.permanent = True
```

### Обработка ошибок и исключений

```python
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

@app.errorhandler(Exception)
def handle_exception(e):
    # Логирование ошибки
    current_app.logger.error(f'Unhandled exception: {e}')
    return render_template('error.html', error=str(e)), 500

# Программный вызов ошибок
from flask import abort

abort(404)  # Вызвать ошибку 404
abort(403, description="Access denied")  # С описанием
```

### Работа с файлами

```python
from flask import send_file, send_from_directory

# Отправка файла
@app.route('/download')
def download():
    return send_file('path/to/file.pdf',
                     as_attachment=True,
                     download_name='report.pdf')

# Отправка из директории
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Обработка загрузки файлов
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return "File uploaded successfully"
```

### Работа с JSON

```python
from flask import jsonify

# Простой JSON ответ
return jsonify({'status': 'success', 'data': [1, 2, 3]})

# JSON с кодом состояния
return jsonify({'error': 'Not found'}), 404

# Кастомная сериализация
@app.route('/api/users')
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

# Парсинг JSON запроса
@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data'}), 400
    
    # Обработка данных
    return jsonify({'received': data})
```

---

## Полезные ссылки

- [Официальная документация Flask](https://flask.palletsprojects.com/en/3.0.x/)
- [Краткое руководство](https://flask.palletsprojects.com/en/3.0.x/quickstart/)
- [Учебник по созданию блога](https://flask.palletsprojects.com/en/3.0.x/tutorial/)
- [API справочник](https://flask.palletsprojects.com/en/3.0.x/api/)
- [Расширения Flask](https://flask.palletsprojects.com/en/3.0.x/extensions/)
