from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def format_price(value):
    if value in (None, ""):
        return "по запросу"
    try:
        return f"{float(value):,.0f}".replace(",", " ") + " ₽"
    except (TypeError, ValueError):
        return str(value)


@register.filter
def distinct(queryset):
    return queryset.distinct()


@register.filter
def get_item(dictionary, key):
    if not isinstance(dictionary, dict):
        return []
    value = dictionary.get(key, dictionary.get(str(key), []))
    return value if value is not None else []


@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (TypeError, ValueError):
        return value


@register.filter
def getattr_safe(obj, attr_name):
    try:
        return getattr(obj, attr_name, "Не указано")
    except Exception:
        return "Ошибка получения данных"


@register.filter
def replace_with_br(value):
    if value is None:
        return ""
    return mark_safe(str(value).replace(",", ",<br>"))


@register.filter
def is_numeric(value):
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


@register.filter
def sort_numeric(values):
    numeric_values = []
    non_numeric_values = []

    for value in values:
        if value and is_numeric(value):
            try:
                numeric_values.append((float(value), value))
            except (TypeError, ValueError):
                non_numeric_values.append(value)
        elif value:
            non_numeric_values.append(value)

    numeric_values.sort(key=lambda item: item[0])
    return [item[1] for item in numeric_values] + non_numeric_values
