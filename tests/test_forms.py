import pytest
from flask import Flask

from app.forms import Form, StringField, PasswordField, DataRequired, Length, EqualTo, Regexp
from app.forms.csrf import generate_csrf_token


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test-key'
    app.config['WTF_CSRF_ENABLED'] = False  # Наша система независима, но для Flask это хорошая практика
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
    """Проверка правильности заполнения данных в полях."""
    with app.app_context():
        data = {'name': '  John  ', 'password': 'pass'}
        form = MockForm(data)
        assert form.name.data == '  John  '
        assert form.password.data == 'pass'


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
