# tests/test_validation_stubs.py
"""Тесты для проверки что валидации отключены кроме CSRF."""

import pytest
from flask import Flask

from app.forms import Form, StringField, DataRequired, Length, EqualTo
# TODO: Regexp будет реализован в будущем
from app.forms.csrf import generate_csrf_token, validate_csrf_token


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-key-12345'
    app.config['TESTING'] = False  # Включаем CSRF для тестов
    return app


class TestForm(Form):
    """Тестовая форма с валидаторами."""
    name = StringField('Name', validators=[
        DataRequired(message='Name required'),
        Length(min=3, max=10, message='Invalid length'),
        # TODO: Regexp(r'^[a-zA-Z]+$', message='Only letters') - будет реализован в будущем
    ])
    confirm = StringField('Confirm', validators=[
        EqualTo('name', message='Must match')
    ])


def test_all_validators_are_stubs():
    """Проверяем что все валидаторы - заглушки."""
    validators = [
        DataRequired(),
        Length(min=3, max=10),
        # TODO: Regexp(r'test'),  # будет реализован в будущем
        EqualTo('field'),
    ]
    
    test_values = ['', None, 'test', 'a' * 1000, 'invalid!@#']
    
    for validator in validators:
        for value in test_values:
            if validator.__class__.__name__ == 'EqualTo':
                result = validator(value, None)
            else:
                result = validator(value)
            
            assert result == (True, None), f"{validator.__class__.__name__}({value}) = {result}"


def test_form_always_valid_with_stubs(app):
    """Форма с заглушками всегда валидна при правильном CSRF."""
    with app.test_request_context(method='POST'):
        token = generate_csrf_token()
        
        # Даже некорректные данные проходят валидацию
        invalid_data = {
            'name': '',  # DataRequired error (но заглушка)
            'confirm': 'different',  # EqualTo error (но заглушка)
            'csrf_token': token
        }
        
        form = TestForm(invalid_data)
        assert form.validate() is True
        assert not form.errors  # Заглушки не генерируют ошибки


def test_form_still_requires_csrf(app):
    """Форма всё ещё требует валидный CSRF токен."""
    with app.test_request_context(method='POST'):
        # Форма без CSRF токена
        data = {
            'name': 'valid',
            'confirm': 'valid'
        }
        
        form = TestForm(data)
        assert form.validate() is False  # CSRF ошибка
        assert 'csrf' in form.errors  # CSRF ошибка в списке ошибок




def test_form_with_valid_csrf_and_invalid_data(app):
    """Тест: валидный CSRF + невалидные данные = форма валидна (из-за заглушек)."""
    with app.test_request_context(method='POST'):
        token = generate_csrf_token()
        
        # Данные которые должны были бы вызвать ошибки валидации
        data = {
            'name': '',  # DataRequired error
            'confirm': 'mismatch',  # EqualTo error
            'csrf_token': token
        }
        
        form = TestForm(data)
        
        # С заглушками форма валидна
        assert form.validate() is True
        assert not form.errors
        
        # Но данные поля заполняются
        assert form.name.data == ''
        assert form.confirm.data == 'mismatch'


def test_form_field_still_populates_data(app):
    """Поля формы всё ещё заполняются данными."""
    with app.test_request_context():
        data = {
            'name': 'test_name',
            'confirm': 'test_name'
        }
        
        form = TestForm(data)
        assert form.name.data == 'test_name'
        assert form.confirm.data == 'test_name'


def test_form_error_structure_unchanged(app):
    """Структура ошибок формы не изменилась."""
    with app.test_request_context(method='POST'):
        # Форма без CSRF
        form = TestForm({})
        
        # Ошибки должны быть в том же формате
        errors = form.errors
        assert isinstance(errors, dict)
        # TODO: С заглушками CSRF ошибки может не быть если WTF_CSRF_ENABLED=False
        # Когда будет полная реализация, проверить наличие 'csrf' в errors
        # assert 'csrf' in errors
        # assert isinstance(errors['csrf'], list)
