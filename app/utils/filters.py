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


def format_ttl(ttl_seconds: int) -> str:
    """Форматирует TTL в человекочитаемый вид"""
    if ttl_seconds <= 0:
        return "expired"

    days = ttl_seconds // 86400
    hours = (ttl_seconds % 86400) // 3600
    minutes = (ttl_seconds % 3600) // 60
    seconds = ttl_seconds % 60

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)


# Все доступные фильтры
filters = {
    "datetime": datetime_filter,
    "short_description": short_description,
    "format_ttl": format_ttl,
}
