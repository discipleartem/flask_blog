import inspect


class Field:
    """Базовое поле формы.

    Атрибуты:
        label: человеко-читаемое название поля
        validators: список валидаторов (классы или функции)
        description: подсказка/описание
        data: текущее значение (из запроса)
        errors: список строк ошибок после validate()
        name: имя поля в форме (устанавливается в Form.__init__)
    """

    def __init__(self, label="", validators=None, description=""):
        self.label = label
        self.validators = validators or []
        self.description = description
        self.data = None
        self.errors = []
        self.name = None  # Устанавливается в Form.__init__

    def validate(self, form):
        """Запускает валидаторы по очереди и собирает ошибки.

        Валидаторы поддерживаются в двух вариантах:
        - validator(value) -> (bool, message)
        - validator(value, form) -> (bool, message)

        Args:
            form: экземпляр формы (нужен для валидаторов типа EqualTo).

        Returns:
            bool: True если поле валидно, иначе False.
        """
        self.errors = []
        is_valid = True

        for validator in self.validators:
            # Проверяем, ожидает ли валидатор доступ к форме (2 аргумента: self, value, form)
            # или только значение (1 аргумент: self, value)
            try:
                # Получаем количество параметров метода __call__
                sig = inspect.signature(validator.__call__)
                params_count = len(sig.parameters)

                if params_count > 1:
                    valid, message = validator(self.data, form)
                else:
                    valid, message = validator(self.data)
            except Exception:
                # Фолбэк для простых функций-валидаторов, если они не классы
                try:
                    valid, message = validator(self.data)
                except TypeError:
                    valid, message = validator(self.data, form)

            if not valid:
                self.errors.append(message)
                is_valid = False

        return is_valid


class StringField(Field):
    """Текстовое поле (пока без специфики, тип нужен для читабельности/расширения)."""


class PasswordField(Field):
    """Поле пароля (тип нужен для семантики; отображение контролируется шаблоном)."""


class TextAreaField(Field):
    """Многострочное текстовое поле."""
