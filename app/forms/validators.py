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


# TODO: Реализовать самописные валидаторы (без сторонних библиотек)
# ==============================================================================
# Заглушки для будущих валидаторов. Временно возвращают True (валидация пройдена)
# ==============================================================================

class Email(Validator):
    """TODO: Проверка корректности email адреса.
    
    Планируемая функциональность:
    - Проверка формата email без использования regex библиотек
    - Валидация домена и локальной части
    - Проверка на запрещенные символы
    """
    
    def __init__(self, message="Некорректный email адрес"):
        super().__init__(message)

    def __call__(self, value):
        # TODO: Реализовать самописную валидацию email
        # Временно всегда считаем валидным
        return True, None


class Username(Validator):
    """TODO: Проверка корректности имени пользователя.
    
    Планируемая функциональность:
    - Проверка формата username#0001
    - Валидация только букв, цифр и символа #
    - Проверка минимальной/максимальной длины
    """
    
    def __init__(self, message="Некорректный формат имени пользователя"):
        super().__init__(message)

    def __call__(self, value):
        # TODO: Реализовать самописную валидацию username
        # Временно всегда считаем валидным
        return True, None


class PasswordStrength(Validator):
    """TODO: Проверка сложности пароля.
    
    Планируемая функциональность:
    - Минимальная длина пароля
    - Обязательные символы: цифры, буквы разного регистра
    - Специальные символы
    - Запрещены простые комбинации
    """
    
    def __init__(self, min_length=8, message="Пароль недостаточно сложный"):
        super().__init__(message)
        self.min_length = min_length

    def __call__(self, value):
        # TODO: Реализовать самописную проверку сложности пароля
        # Временно всегда считаем валидным
        return True, None


class UniqueUsername(Validator):
    """TODO: Проверка уникальности имени пользователя в базе данных.
    
    Планируемая функциональность:
    - Запрос к базе данных для проверки существования username
    - Кэширование результатов для оптимизации
    - Учёт текущего пользователя при редактировании профиля
    """
    
    def __init__(self, message="Такое имя пользователя уже существует"):
        super().__init__(message)

    def __call__(self, value, form):
        # TODO: Реализовать проверку уникальности username в БД
        # Временно всегда считаем валидным
        return True, None


class Slug(Validator):
    """TODO: Проверка корректности slug для URL.
    
    Планируемая функциональность:
    - Только буквы, цифры, дефисы и подчёркивания
    - Нет пробелов и специальных символов
    - Не начинается/заканчивается дефисом
    """
    
    def __init__(self, message="Некорректный формат slug"):
        super().__init__(message)

    def __call__(self, value):
        # TODO: Реализовать самописную валидацию slug
        # Временно всегда считаем валидным
        return True, None


class NumberRange(Validator):
    """TODO: Проверка числового значения в диапазоне.
    
    Планируемая функциональность:
    - Проверка минимального и максимального значения
    - Работа с int и float
    - Обработка нечисловых значений
    """
    
    def __init__(self, min=None, max=None, message="Значение вне допустимого диапазона"):
        super().__init__(message)
        self.min = min
        self.max = max

    def __call__(self, value):
        # TODO: Реализовать самописную проверку числового диапазона
        # Временно всегда считаем валидным
        return True, None


class URL(Validator):
    """TODO: Проверка корректности URL.
    
    Планируемая функциональность:
    - Проверка формата URL (протокол, домен, путь)
    - Валидация протоколов (http, https)
    - Запрет небезопасных протоколов
    """
    
    def __init__(self, message="Некорректный URL"):
        super().__init__(message)

    def __call__(self, value):
        # TODO: Реализовать самописную валидацию URL
        # Временно всегда считаем валидным
        return True, None
