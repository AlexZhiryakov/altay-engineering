from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def format_price(value):
    return f"{value:,.0f}".replace(",", " ") + " ₽"

@register.filter
def distinct(queryset):
    return queryset.distinct()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def mul(value, arg):
    """Фильтр для умножения значений в шаблоне."""
    try:
        return float(value) * int(arg)
    except (ValueError, TypeError):
        return value  # Если ошибка, возвращаем оригинальное значение
    
@register.filter
def getattr_safe(obj, attr_name):
    """Безопасно получает атрибут объекта"""
    try:
        return getattr(obj, attr_name, "Не указано")
    except Exception:
        return "Ошибка получения данных"
    
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])

@register.filter
def replace_with_br(value):
    if value is None:
        return ""
    # Преобразуем в строку, если это не строка
    str_value = str(value) if not isinstance(value, str) else value
    return mark_safe(str_value.replace(",", ",<br>"))

@register.filter
def get_item(dictionary, key):
    return dictionary.get(str(key))

@register.filter
def is_numeric(value):
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

@register.filter
def sort_numeric(values):
    numeric_values = []
    non_numeric_values = []
    
    for value in values:
        if value and is_numeric(value):
            try:
                # Пробуем преобразовать в float для сортировки
                numeric_values.append((float(value), value))
            except (ValueError, TypeError):
                non_numeric_values.append(value)
        elif value:
            non_numeric_values.append(value)
    
    # Сортируем числовые значения
    numeric_values.sort(key=lambda x: x[0])
    
    # Возвращаем отсортированные числовые значения и остальные
    return [v[1] for v in numeric_values] + non_numeric_values