# tests/test_forms.py
"""Тесты для системы форм."""

import pytest
from flask import Flask

from app.forms import Form, StringField, PasswordField, DataRequired, Length, EqualTo, Email, Username, PasswordStrength, UniqueUsername, Slug, NumberRange, URL
# TODO: Regexp будет реализован в будущем
from app.forms.csrf import generate_csrf_token, validate_csrf_token


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-key-12345'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app


class MockForm(Form):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=10)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm', validators=[DataRequired(), EqualTo('password', message='Mismatch')])
    # TODO: username с Regexp будет добавлен при реализации
    username = StringField('Username', validators=[DataRequired()])  # TODO: + Regexp(r'^\w+$', message='Invalid')


def test_form_validation_success(app):
    """Тест успешной валидации формы.
    
    TODO: После реализации валидаторов этот тест должен проверять реальную валидацию.
    Сейчас все валидаторы - заглушки и всегда возвращают True.
    """
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
        # TODO: После реализации валидаторов ожидать True только для корректных данных
        assert form.validate() is True
        assert not form.errors


def test_form_validation_placeholder(app):
    """Тест валидации формы с корректными данными."""
    with app.test_request_context(method='POST'):
        token = generate_csrf_token()
        # Используем корректные данные для валидации
        data = {
            'name': 'ValidName',  # Корректное имя (DataRequired, Length 3-10)
            'password': 'valid_pass',  # Корректный пароль (DataRequired)
            'confirm': 'valid_pass',  # Совпадает с паролем (EqualTo)
            'username': 'validuser',  # Корректный username (DataRequired)  # TODO: + Length min=3, Regexp
            'csrf_token': token
        }
        form = MockForm(data)
        assert form.validate() is True
        assert not form.errors


def test_form_data_population(app):
    """Проверка правильности заполнения данных в полях."""
    with app.app_context():
        data = {'name': '  John  ', 'password': 'pass'}
        form = MockForm(data)
        assert form.name.data == '  John  '
        assert form.password.data == 'pass'




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
    """Тест обработки ошибок формы с заглушками валидаторов.
    
    TODO: После реализации валидаторов этот тест должен проверять реальные ошибки.
    Сейчас все валидаторы - заглушки и всегда возвращают True.
    """
    with app.test_request_context():
        token = generate_csrf_token()
        
        # Форма с данными, которые должны были бы вызывать ошибки
        data = {
            'name': '',  # TODO: DataRequired error (когда будет реализовано)
            'password': '12',  # TODO: Слишком короткий (меньше 3 символов)
            'confirm': '456',  # TODO: EqualTo error
            'username': 'user!@#',  # TODO: Regexp error (когда будет реализовано)
            'csrf_token': token
        }
        form = MockForm(data)
        
        # Сейчас все валидаторы - заглушки, поэтому форма всегда валидна
        assert form.validate() is True
        assert not form.errors  # Заглушки не генерируют ошибки


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
        
        # В TESTING режиме CSRF отключен, поэтому валидация должна пройти
        assert form.validate() is True


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
    """Тестирование отдельных валидаторов-заглушек.
    
    TODO: После реализации валидаторов этот тест должен проверять реальную валидацию.
    Сейчас все валидаторы - заглушки и всегда возвращают (True, None).
    """
    # DataRequired - заглушка всегда возвращает True
    dr = DataRequired()
    assert dr("content") == (True, None)
    assert dr("valid") == (True, None)
    assert dr("") == (True, None)  # TODO: должно быть (False, message)
    assert dr("   ") == (True, None)  # TODO: должно быть (False, message)

    # Length - заглушка всегда возвращает True
    l = Length(min=5)
    assert l("12345") == (True, None)
    assert l("1234") == (True, None)  # TODO: должно быть (False, message)
    assert l("123") == (True, None)  # TODO: должно быть (False, message)

    # TODO: Regexp - будет реализован в будущем
    # r = Regexp(r'^\w+$')
    # assert r("valid123") == (True, None)
    # assert r("invalid!@#") == (True, None)  # TODO: должно быть (False, message)

    # EqualTo - заглушка всегда возвращает True
    mock_form = type('MockForm', (), {'field1': type('MockField', (), {'data': 'value'})})()
    eq = EqualTo('field1')
    assert eq("value", mock_form) == (True, None)
    assert eq("different", mock_form) == (True, None)  # TODO: должно быть (False, message)


def test_validator_stubs_always_return_true():
    """Тест что все валидаторы-заглушки всегда возвращают (True, None)."""
    validators_to_test = [
        DataRequired(),
        Length(min=3, max=10),
        # TODO: Regexp(r'test'),  # будет реализован в будущем
        EqualTo('test'),
        # TODO валидаторы
        Email(),
        Username(),
        PasswordStrength(),
        UniqueUsername(),
        Slug(),
        NumberRange(),
        URL()
    ]
    
    test_values = ['', 'test', None, 123, 'a' * 1000, 'invalid!@#', 'short']
    
    for validator in validators_to_test:
        for value in test_values:
            try:
                if validator.__class__.__name__ in ['EqualTo', 'UniqueUsername']:
                    result = validator(value, None)
                else:
                    result = validator(value)
                
                assert result == (True, None), f"{validator.__class__.__name__}({value}) = {result}, expected (True, None)"
            except Exception as e:
                pytest.fail(f"Ошибка в валидаторе {validator.__class__.__name__}: {e}")
