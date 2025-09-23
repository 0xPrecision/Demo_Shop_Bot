import re

def validate_name(name: str) -> bool:
    """
    Validates that the name consists only of letters (Cyrillic or Latin), spaces, or hyphens,
    and is at least 2 characters long.
	"""
    name = name.strip()
    return bool(re.fullmatch(r"[A-Za-zА-Яа-яЁё\s\-]+", name)) and len(name) >= 2


def validate_phone(phone: str) -> bool:
    """
    Validates that the phone number contains only digits and is 10–15 characters long.
	"""
    phone = phone.strip()
    return phone.isdigit() and 10 <= len(phone) <= 15

def validate_address(address: str) -> bool:
    """
    Validates that the address contains letters, digits, spaces, simple punctuation, and is at least 5 characters long.
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
    Formats the name: capitalizes each word.
	"""
    return name.strip().title()
