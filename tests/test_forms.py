# tests/test_forms.py
"""Тесты для системы форм."""

import pytest
from flask import Flask

from app.forms import Form, StringField, PasswordField, DataRequired, Length, EqualTo, Regexp
from app.forms.csrf import generate_csrf_token, validate_csrf_token


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-key-12345'
    app.config['WTF_CSRF_ENABLED'] = False
    return app


class MockForm(Form):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=10)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm', validators=[DataRequired(), EqualTo('password', message='Mismatch')])
    username = StringField('Username', validators=[DataRequired(), Regexp(r'^\w+$', message='Invalid')])


def test_form_validation_success(app):
    """Тест успешной валидации формы с правильными данными и CSRF."""
    with app.test_request_context(method='POST'):
        token = generate_csrf_token()
        data = {
            'name': 'Admin',
            'password': 'secret_password',
            'confirm': 'secret_password',
            'username': 'user_123',
            'csrf_token': token
        }
        form = MockForm(data)
        assert form.validate() is True
        assert not form.errors


def test_form_validation_failure(app):
    """Тест ошибок валидации: пустые поля, короткая длина, несовпадение паролей."""
    with app.test_request_context(method='POST'):
        token = generate_csrf_token()
        # Случай 1: Некорректные данные
        data = {
            'name': 'Ad',  # Слишком короткое
            'password': '123',
            'confirm': '321',  # Не совпадает
            'username': 'user!@#',  # Не проходит Regexp
            'csrf_token': token
        }
        form = MockForm(data)
        assert form.validate() is False
        assert 'name' in form.errors
        assert 'confirm' in form.errors
        assert 'username' in form.errors

        # Случай 2: Пустые данные (проверка DataRequired)
        form_empty = MockForm({'csrf_token': token})
        assert form_empty.validate() is False
        assert 'password' in form_empty.errors
        assert 'name' in form_empty.errors
def test_form_data_population(app):
    """Проверка правильности заполнения данных в полях."""
    with app.app_context():
        data = {'name': '  John  ', 'password': 'pass'}
        form = MockForm(data)
        assert form.name.data == '  John  '
        assert form.password.data == 'pass'


def test_csrf_token_validation(app):
    """Тест валидации CSRF токена."""
    with app.test_request_context():
        # Генерация токена
        token = generate_csrf_token()
        
        # Валидация правильного токена
        assert validate_csrf_token(token) is True
        
        # Валидация неправильного токена
        assert validate_csrf_token('wrong_token') is False
        assert validate_csrf_token('') is False
        assert validate_csrf_token(None) is False


def test_form_field_access(app):
    """Тест доступа к полям формы."""
    with app.test_request_context():
        form = MockForm()
        
        # Проверка существования полей
        assert hasattr(form, 'name')
        assert hasattr(form, 'password')
        assert hasattr(form, 'confirm')
        assert hasattr(form, 'username')
        
        # Проверка типов полей
        assert isinstance(form.name, StringField)
        assert isinstance(form.password, PasswordField)
        assert isinstance(form.confirm, PasswordField)
        assert isinstance(form.username, StringField)


def test_form_error_handling(app):
    """Тест обработки ошибок формы."""
    with app.test_request_context():
        token = generate_csrf_token()
        
        # Форма с ошибками
        data = {
            'name': '',  # DataRequired error
            'password': '12',  # Слишком короткий (меньше 3 символов)
            'confirm': '456',  # EqualTo error
            'username': 'user!@#',  # Regexp error
            'csrf_token': token
        }
        form = MockForm(data)
        
        # Валидация должна провалиться
        assert form.validate() is False
        
        # Проверка наличия ошибок в полях
        assert 'name' in form.errors
        assert 'confirm' in form.errors
        assert 'username' in form.errors
        # Поле password может не иметь ошибки (нет валидатора Length)
        # Проверяем только если есть ошибка
        if 'password' in form.errors:
            assert len(form.errors['password']) > 0
        
        # Проверка сообщений об ошибках
        assert len(form.errors['name']) > 0
        assert len(form.errors['confirm']) > 0
        assert len(form.errors['username']) > 0
        # Проверяем ошибки password только если они есть
        if 'password' in form.errors:
            assert len(form.errors['password']) > 0


def test_form_without_csrf(app):
    """Тест формы без CSRF токена."""
    with app.test_request_context():
        # Форма без CSRF токена
        data = {
            'name': 'ValidName',
            'password': 'validpassword',
            'confirm': 'validpassword',
            'username': 'validuser'
        }
        form = MockForm(data)
        
        # Форма должна быть невалидной без CSRF
        assert form.validate() is False


def test_form_with_extra_fields(app):
    """Тест формы с дополнительными полями."""
    with app.test_request_context():
        token = generate_csrf_token()
        
        # Форма с дополнительными полями
        data = {
            'name': 'ValidName',
            'password': 'validpassword',
            'confirm': 'validpassword',
            'username': 'validuser',
            'csrf_token': token,
            'extra_field': 'extra_value'  # Дополнительное поле
        }
        form = MockForm(data)
        
        # Форма должна быть валидной (дополнительные поля игнорируются)
        assert form.validate() is True
        assert not form.errors


def test_validators_standalone():
    """Тестирование отдельных валидаторов без привязки к форме (где возможно)."""
    # DataRequired
    dr = DataRequired()
    assert dr("content")[0] is True
    assert dr("  ")[0] is False
    assert dr("")[0] is False

    # Length
    l = Length(min=5)
    assert l("12345")[0] is True
    assert l("1234")[0] is False

    # Regexp
    r = Regexp(r'^\d+$')
    assert r("123")[0] is True
    assert r("abc")[0] is False
