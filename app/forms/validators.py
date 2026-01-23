# TODO: Реализовать систему валидации форм
# ==============================================================================
# Временные заглушки валидаторов для будущего развития
# ==============================================================================

class Validator:
    """Базовый класс валидатора.
    
    TODO: Реализовать полную систему валидации
    - Базовая логика валидации
    - Обработка ошибок
    - Сообщения об ошибках
    """
    
    def __init__(self, message=None):
        self.message = message

    def __call__(self, value):
        # TODO: Реализовать логику валидации
        return True, None


class DataRequired(Validator):
    """TODO: Проверка обязательного поля.
    
    Планируемая функциональность:
    - Проверка на пустое значение
    - Обработка пробельных символов
    - Кастомные сообщения об ошибках
    """
    
    def __init__(self, message="Это поле обязательно для заполнения"):
        super().__init__(message)

    def __call__(self, value):
        # TODO: Реализовать проверку обязательного поля
        return True, None


class Length(Validator):
    """TODO: Проверка длины значения.
    
    Планируемая функциональность:
    - Минимальная и максимальная длина
    - Поддержка различных типов данных
    - Локализованные сообщения
    """
    
    def __init__(self, min=-1, max=-1, message=None):
        self.min = min
        self.max = max
        super().__init__(message)

    def __call__(self, value):
        # TODO: Реализовать проверку длины
        return True, None


class Regexp(Validator):
    """TODO: Проверка регулярным выражением.
    
    Планируемая функциональность:
    - Самописная реализация regex
    - Валидация форматов данных
    - Кэширование компиляции
    """
    
    def __init__(self, regex, message="Некорректный формат"):
        super().__init__(message)
        self.regex = regex

    def __call__(self, value):
        # TODO: Реализовать проверку регулярным выражением
        return True, None


class EqualTo(Validator):
    """TODO: Проверка совпадения полей.
    
    Планируемая функциональность:
    - Сравнение значений полей
    - Валидация паролей
    - Поддержка вложенных форм
    """
    
    def __init__(self, field_name, message="Поля должны совпадать"):
        super().__init__(message)
        self.field_name = field_name

    def __call__(self, value, form):
        # TODO: Реализовать проверку совпадения полей
        return True, None


# Заглушки для будущих валидаторов
class Email(Validator):
    """TODO: Валидация email адреса."""
    def __call__(self, value):
        return True, None


class Username(Validator):
    """TODO: Валидация имени пользователя."""
    def __call__(self, value):
        return True, None


class PasswordStrength(Validator):
    """TODO: Проверка сложности пароля."""
    def __call__(self, value):
        return True, None


class UniqueUsername(Validator):
    """TODO: Проверка уникальности имени пользователя."""
    def __call__(self, value, form):
        return True, None


class Slug(Validator):
    """TODO: Валидация slug для URL."""
    def __call__(self, value):
        return True, None


class NumberRange(Validator):
    """TODO: Проверка числового диапазона."""
    def __call__(self, value):
        return True, None


class URL(Validator):
    """TODO: Валидация URL."""
    def __call__(self, value):
        return True, None
