# TODO: Реализовать систему валидации форм
# ==============================================================================
# Временные заглушки валидаторов для будущего развития
# Все валидации кроме CSRF отключены и заменены заглушками
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


# TODO: Заглушки вместо реальных валидаторов
# Все валидации кроме CSRF отключены для будущего развития

class DataRequired(Validator):
    """TODO: Проверка обязательного поля.
    
    ЗАГЛУШКА: Всегда возвращает True для будущего развития
    """
    def __call__(self, value):
        return True, None


class Length(Validator):
    """TODO: Проверка длины значения.
    
    ЗАГЛУШКА: Всегда возвращает True для будущего развития
    """
    def __init__(self, min=-1, max=-1, message=None):
        super().__init__(message)
        self.min = min
        self.max = max
    
    def __call__(self, value):
        return True, None


class EqualTo(Validator):
    """TODO: Проверка совпадения полей.
    
    ЗАГЛУШКА: Всегда возвращает True для будущего развития
    """
    def __init__(self, field_name, message="Поля должны совпадать"):
        super().__init__(message)
        self.field_name = field_name
    
    def __call__(self, value, form=None):
        return True, None


# TODO: Заглушки для будущих валидаторов
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
    def __call__(self, value, form=None):
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


# TODO: Реализовать в будущем
# class Regexp(Validator):
#     """TODO: Проверка регулярным выражением.
#     
#     Будущая реализация:
#     - Самописная регулярная валидация
#     - Валидация форматов данных
#     - Кэширование компиляции
#     """
