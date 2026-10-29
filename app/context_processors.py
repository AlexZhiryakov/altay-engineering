from django.conf import settings
from django.http import HttpRequest

from .site_info import SITE


def public_settings(request: HttpRequest) -> dict:
    return {
        "yandex_maps_api_key": settings.YANDEX_MAPS_API_KEY,
        "site": SITE,
    }


def cart_count(request: HttpRequest) -> dict[str, int]:
    """Число позиций в корзине. Пустая сессия не должна ронять страницу."""
    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    return {"cart_count": len(cart)}
