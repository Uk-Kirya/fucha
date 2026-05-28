from datetime import datetime


def datetime_filter(value: datetime):
    """
    Фильтр для русского формата даты: 08 окт 2025 в 20:34
    """
    if not value:
        return ""

    months = [
        "января",
        "февраля",
        "марта",
        "апреля",
        "мая",
        "июня",
        "июля",
        "августа",
        "сентября",
        "октября",
        "ноября",
        "декабря",
    ]

    return f"{value.day} {months[value.month - 1][:3]} {value.year} в {value.hour:02d}:{value.minute:02d}"


def short_description(value: str) -> str:
    if value:
        if len(value) > 70:
            return value[:70] + '...'
        return value
    else:
        return ''


# Все доступные фильтры
filters = {
    "datetime": datetime_filter,
    "short_description": short_description
}
