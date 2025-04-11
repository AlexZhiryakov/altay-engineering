from django.shortcuts import get_object_or_404
from app.models import Product

# Количество товаров в корзине
def cart_count(request):
    cart = len(request.session["cart"])
    return {"cart_count": cart}