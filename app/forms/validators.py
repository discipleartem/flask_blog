import re


class Validator:
    """Базовый класс валидатора.

    Валидатор вызывается как функция и возвращает:
        (True, None) — если ок
        (False, "сообщение") — если ошибка
    """

    def __init__(self, message=None):
        self.message = message

    def __call__(self, value):
        raise NotImplementedError("Валидатор должен реализовать метод __call__")


class DataRequired(Validator):
    """Проверяет, что значение присутствует и не является пустой строкой."""

    def __init__(self, message="Это поле обязательно для заполнения"):
        super().__init__(message)

    def __call__(self, value):
        if not value or (isinstance(value, str) and not value.strip()):
            return False, self.message
        return True, None


class Length(Validator):
    """Проверяет длину значения (обычно строки) по min/max."""

    def __init__(self, min=-1, max=-1, message=None):
        self.min = min
        self.max = max
        if not message:
            if min != -1 and max != -1:
                message = f"Длина должна быть от {min} до {max} символов"
            elif min != -1:
                message = f"Длина должна быть не менее {min} символов"
            else:
                message = f"Длина должна быть не более {max} символов"
        super().__init__(message)

    def __call__(self, value):
        length = len(value) if value else 0
        if (self.min != -1 and length < self.min) or (self.max != -1 and length > self.max):
            return False, self.message
        return True, None


class Regexp(Validator):
    """Проверяет значение регулярным выражением (match от начала строки)."""

    def __init__(self, regex, message="Некорректный формат"):
        super().__init__(message)
        self.regex = re.compile(regex)

    def __call__(self, value):
        if not self.regex.match(value or ""):
            return False, self.message
        return True, None


class EqualTo(Validator):
    """Проверяет, что значение совпадает со значением другого поля формы."""

    def __init__(self, field_name, message="Поля должны совпадать"):
        super().__init__(message)
        self.field_name = field_name

    def __call__(self, value, form):
        # Получаем другое поле из формы по имени
        other_field = getattr(form, self.field_name, None)
        if other_field is None or value != other_field.data:
            return False, self.message
        return True, None
