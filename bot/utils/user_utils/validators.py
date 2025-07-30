import re

def validate_name(name: str) -> bool:
    """
    Проверяет, что имя состоит только из букв (русские и латинские), пробелов или дефисов,
    и длина не менее 2 символов.
    """
    name = name.strip()
    return bool(re.fullmatch(r"[A-Za-zА-Яа-яЁё\s\-]+", name)) and len(name) >= 2


def validate_phone(phone: str) -> bool:
    """
    Проверяет, что телефон состоит только из цифр и длина от 10 до 15 знаков.
    """
    phone = phone.strip()
    return phone.isdigit() and 10 <= len(phone) <= 15

def validate_address(address: str) -> bool:
    """
    Проверяет, что адрес состоит из букв, цифр, пробелов и простых знаков препинания, длина не менее 5 символов.
    """
    address = address.strip()
    return bool(re.fullmatch(r"[A-Za-zА-Яа-яЁё0-9\s,\.\-\№]+", address)) and len(address) >= 5

def is_profile_complete(user_profile) -> bool:
    for field in ('full_name', 'phone', 'address'):
        value = getattr(user_profile, field, None)
        if not value or str(value).strip() in ('-', '', None):
            return False
    return True


def format_name(name: str) -> str:
    """
    Форматирует имя: каждое слово с большой буквы.
    """
    return name.strip().title()
