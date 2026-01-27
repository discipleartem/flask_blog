"""Формы для аутентификации пользователей."""

from typing import Any, Optional

from . import Form, StringField, PasswordField, DataRequired, Length

# TODO: Regexp будет реализован в будущем для валидации формата данных


class RegistrationForm(Form):
    """Форма регистрации нового пользователя."""

    username = StringField(
        "Имя пользователя",
        validators=[
            DataRequired(message="Имя пользователя обязательно"),
            Length(
                min=3,
                max=20,
                message="Имя пользователя должно быть от 3 до 20 символов",
            ),
            # TODO: Добавить Regexp(
            #     r'^[a-zA-Z0-9_]+$',
            #     message='Имя пользователя может содержать только буквы, '
            #             'цифры и подчёркивания'
            # )
            # TODO: Добавить Regexp(r'^(?!.*#).*$',
            #     message='Имя пользователя не должно содержать символ #')
        ],
    )

    password = PasswordField(
        "Пароль",
        validators=[
            DataRequired(message="Пароль обязателен"),
            Length(min=4, max=128, message="Пароль должен быть от 4 до 128 символов"),
        ],
    )


class LoginForm(Form):
    """Форма входа пользователя."""

    username = StringField(
        "Имя пользователя",
        validators=[
            DataRequired(message="Имя пользователя обязательно"),
            # TODO: Добавить Regexp(r'^[a-zA-Z0-9_]+#\d{4}$', message='Формат:
            # имя#0001')
        ],
    )

    password = PasswordField(
        "Пароль", validators=[DataRequired(message="Пароль обязателен")]
    )

    def __init__(self, formdata: Optional[Any] = None, **kwargs: Any) -> None:
        super().__init__(formdata, **kwargs)
        # Если форма отправлена с login_username, используем его как username
        if formdata and "login_username" in formdata:
            self.username.data = formdata["login_username"]
        # Если форма отправлена с login_password, используем его как password
        if formdata and "login_password" in formdata:
            self.password.data = formdata["login_password"]
