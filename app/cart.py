from django.conf import settings
from django.http import JsonResponse
from .models import Product

def add(request):
    product_id = request.GET.get("product_id")
    action = request.GET.get("action", "add")

    if not product_id:
        return JsonResponse({"error": "Нет product_id"}, status=400)

    cart = request.session.get("cart", {})

    if action == "add":
        cart[product_id] = cart.get(product_id, 0) + 1  # Увеличиваем количество
    elif action == "remove":
        if product_id in cart:
            cart[product_id] -= 1  # Уменьшаем количество
            if cart[product_id] <= 0:
                del cart[product_id]  # Удаляем, если количество 0
    elif action == "delete":
        cart.pop(product_id, None)  # Удаляем товар

    request.session["cart"] = cart
    request.session.modified = True

    # Пересчитываем общую сумму корзины
    cart_products = {int(pid): Product.objects.get(id=int(pid)) for pid in cart.keys()}
    total_cart_price = sum(product.price * qty for pid, product in cart_products.items() for qty in [cart[str(pid)]])

    return JsonResponse({
        "success": True,
        "quantity": cart.get(product_id, 0),
        "total_price": total_cart_price
    })