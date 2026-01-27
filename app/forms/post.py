"""Формы для работы с постами блога."""

from . import Form, StringField, TextAreaField, DataRequired, Length


class PostForm(Form):
    """Форма для создания и редактирования поста."""

    title = StringField(
        "Заголовок",
        validators=[
            DataRequired(message="Заголовок обязателен"),
            Length(
                min=1, max=200, message="Заголовок должен быть от 1 до 200 символов"
            ),
        ],
    )

    content = TextAreaField(
        "Содержание",
        validators=[
            DataRequired(message="Содержание обязательно"),
            Length(
                min=10,
                max=5000,
                message="Содержание должно быть от 10 до 5000 символов",
            ),
        ],
    )
