"""Формы для работы с комментариями."""
from . import Form, TextAreaField, DataRequired, Length


class CommentForm(Form):
    """Форма для добавления комментария к посту."""
    
    content = TextAreaField(
        'Комментарий',
        validators=[
            DataRequired(message='Текст комментария обязателен'),
            Length(min=3, max=1000, message='Комментарий должен быть от 3 до 1000 символов')
        ]
    )
