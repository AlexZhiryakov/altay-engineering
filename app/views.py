import logging
import threading
from io import BytesIO
from pathlib import Path
from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

from .models import Category, Product, Request, RequestItem
from .site_info import SITE

logger = logging.getLogger(__name__)
NOVOSIBIRSK = ZoneInfo("Asia/Novosibirsk")


def register_fonts() -> None:
    regular = Path(settings.BASE_DIR) / "static" / "fonts" / "DejaVuSans.ttf"
    bold = Path(settings.BASE_DIR) / "static" / "fonts" / "DejaVuSans-Bold.ttf"
    if not regular.is_file():
        raise FileNotFoundError(f"Не найден шрифт {regular}")
    pdfmetrics.registerFont(TTFont("DejaVuSans", str(regular)))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", str(bold if bold.is_file() else regular)))


def format_price(value) -> str:
    if value is None or value == "по запросу":
        return "по запросу"
    try:
        return f"{int(value):,}".replace(",", " ") + " ₽"
    except (TypeError, ValueError):
        return str(value)


def mainPage(request: HttpRequest) -> HttpResponse:
    return render(request, "app/mainPage.html")


def download_file(request: HttpRequest) -> HttpResponseNotFound:
    # Старый PDF с реальными реквизитами бизнеса больше не отдаём.
    return HttpResponseNotFound("Файл реквизитов недоступен: это демонстрационный pet-проект.")


def privacyPolicy(request: HttpRequest) -> HttpResponse:
    return render(request, "app/privacyPolicy.html")


def termsOfUse(request: HttpRequest) -> HttpResponse:
    return render(request, "app/termsOfUse.html")


def cookiePolicy(request: HttpRequest) -> HttpResponse:
    return render(request, "app/cookiePolicy.html")


def refundPolicy(request: HttpRequest) -> HttpResponse:
    return render(request, "app/refundPolicy.html")


def aboutCompany(request: HttpRequest) -> HttpResponse:
    return render(request, "app/company/aboutCompany.html")


def companyDetails(request: HttpRequest) -> HttpResponse:
    return render(request, "app/company/companyDetails.html")


def _products_in_cart(cart: dict) -> tuple[dict[Product, int], float, bool]:
    cart_items: dict[Product, int] = {}
    total = 0.0
    has_price_request = False
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.prefetch_related("images").get(id=int(product_id))
            qty = int(quantity)
        except (Product.DoesNotExist, TypeError, ValueError):
            continue
        cart_items[product] = qty
        if product.price is not None:
            total += float(product.price) * qty
        else:
            has_price_request = True
    return cart_items, total, has_price_request


def shoppingCart(request: HttpRequest) -> HttpResponse:
    cart_items, total_cart_price, _has_request = _products_in_cart(request.session.get("cart", {}))
    return render(
        request,
        "app/shoppingCart.html",
        {
            "cart_items": cart_items,
            "total_cart_price": total_cart_price if cart_items else None,
        },
    )


@require_POST
def add_to_cart(request: HttpRequest) -> JsonResponse:
    product_id = request.POST.get("product_id")
    try:
        product = get_object_or_404(Product, id=int(product_id))
    except (TypeError, ValueError):
        return JsonResponse({"error": "Нет product_id"}, status=400)

    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    key = str(product.id)
    if key in cart:
        del cart[key]
        in_cart = False
    else:
        cart[key] = 1
        in_cart = True

    request.session["cart"] = cart
    request.session.modified = True
    return JsonResponse({"in_cart": in_cart})


@require_POST
def update_cart(request: HttpRequest) -> JsonResponse:
    product_id = request.POST.get("product_id")
    action = request.POST.get("action")
    try:
        product = get_object_or_404(Product, id=int(product_id))
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        return JsonResponse({"error": "Некорректные данные"}, status=400)

    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    key = str(product.id)

    if action == "set":
        if quantity <= 0:
            cart.pop(key, None)
        else:
            cart[key] = quantity
    elif action == "remove":
        cart.pop(key, None)

    request.session["cart"] = cart
    request.session.modified = True

    total_cart_price = 0
    for pid, qty in cart.items():
        try:
            item = Product.objects.get(id=int(pid))
            item_qty = int(qty)
        except (Product.DoesNotExist, TypeError, ValueError):
            continue
        if item.price is not None:
            total_cart_price += float(item.price) * item_qty

    if key not in cart:
        return JsonResponse(
            {"success": True, "quantity": 0, "total_price": 0, "total_cart_price": total_cart_price}
        )

    total_price = float(product.price) * cart[key] if product.price is not None else None
    return JsonResponse(
        {
            "success": True,
            "quantity": cart[key],
            "total_price": total_price,
            "total_cart_price": total_cart_price,
        }
    )


def placeOrder(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip().lower()
        comment = request.POST.get("comment", "").strip()
        privacy_policy = request.POST.get("privacy_policy") == "on"

        if not all([name, phone, email]):
            return _order_error(request, "Пожалуйста, заполните все обязательные поля")
        try:
            validate_email(email)
        except ValidationError:
            return _order_error(request, "Укажите корректный email")
        if not privacy_policy:
            return _order_error(request, "Необходимо согласие с политикой конфиденциальности")

        cart = request.session.get("cart", {})
        if not cart:
            return _order_error(request, "Ваша корзина пуста", "shopping-cart")

        current_time = timezone.now().astimezone(NOVOSIBIRSK)
        request_obj = Request.objects.create(
            customer_name=name,
            customer_phone=phone,
            customer_email=email,
            comment=comment,
            is_processed=False,
            privacy_policy_accepted=True,
            privacy_policy_accepted_at=current_time,
            created_at=current_time,
        )

        total_price = 0
        has_price_request = False
        cart_products = []
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=int(product_id))
                qty = int(quantity)
            except (Product.DoesNotExist, TypeError, ValueError):
                continue
            RequestItem.objects.create(
                request=request_obj,
                product=product,
                quantity=qty,
                price=product.price,
                product_name=product.name,
                product_description=product.description,
            )
            item_total = float(product.price) * qty if product.price else 0
            cart_products.append(
                {
                    "name": product.name,
                    "quantity": qty,
                    "price": product.price if product.price else "по запросу",
                    "total": item_total if product.price else "по запросу",
                }
            )
            if product.price:
                total_price += item_total
            else:
                has_price_request = True

        request_obj.total_price = total_price if total_price > 0 else None
        request_obj.has_price_request_items = has_price_request
        request_obj.save()

        try:
            pdf_content = generate_order_pdf(request_obj, cart_products)
            if pdf_content:
                worker = threading.Thread(
                    target=send_order_email_with_pdf,
                    args=(request_obj, pdf_content),
                    daemon=True,
                )
                worker.start()
                if settings.DEBUG:
                    worker.join(timeout=5)
        except Exception:
            logger.exception("Ошибка при генерации PDF")

        request.session["cart"] = {}
        request.session["last_request_id"] = request_obj.id
        request.session.modified = True
        return redirect("request-success")

    cart = request.session.get("cart", {})
    if not cart:
        return _order_error(request, "Ваша корзина пуста", "shopping-cart")

    cart_items, total_cart_price, has_price_request_items = _products_in_cart(cart)
    return render(
        request,
        "app/placeOrder.html",
        {
            "cart_items": cart_items,
            "total_cart_price": total_cart_price if cart_items else None,
            "has_price_request_items": has_price_request_items,
        },
    )


def _order_error(request: HttpRequest, text: str, target: str = "place-order") -> HttpResponse:
    messages.error(request, text)
    return redirect(target)


def _draw_footer(pdf, left_margin: int, y_pos: int, privacy_date: str, order: Request) -> None:
    pdf.setFont("DejaVuSans", 8)
    accepted = "Да" if order.privacy_policy_accepted else "Нет"
    pdf.drawString(left_margin, y_pos, f"Согласие с политикой конфиденциальности: {accepted}")
    pdf.drawString(left_margin, y_pos - 15, f"Дата согласия: {privacy_date}")
    pdf.drawString(left_margin, y_pos - 30, "Документ сформирован автоматически")


def generate_order_pdf(order: Request, cart_products: list[dict]) -> bytes | None:
    try:
        register_fonts()
        created_at = order.created_at.astimezone(NOVOSIBIRSK).strftime("%d.%m.%Y %H:%M")
        privacy_date = order.privacy_policy_accepted_at.astimezone(NOVOSIBIRSK).strftime("%d.%m.%Y %H:%M")

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        left_margin = 50
        right_margin = width - 50
        top_margin = height - 50
        bottom_margin = 100
        line_height = 20
        section_spacing = 30

        pdf.setFont("DejaVuSans-Bold", 18)
        pdf.drawString(left_margin, top_margin, SITE.brand_name)
        pdf.setFont("DejaVuSans", 10)
        pdf.drawString(left_margin, top_margin - line_height, f"Дата: {created_at}")

        current_y = top_margin - line_height * 2 - 10
        pdf.setFont("DejaVuSans-Bold", 14)
        pdf.drawString(left_margin, current_y, f"Заказ №{order.id}")
        current_y -= line_height + 10
        pdf.setFont("DejaVuSans-Bold", 12)
        pdf.drawString(left_margin, current_y, "Информация о клиенте:")
        current_y -= line_height

        client_data = [
            ["ФИО:", order.customer_name],
            ["Телефон:", order.customer_phone],
            ["Email:", order.customer_email],
            ["Комментарий:", order.comment or "-"],
        ]
        client_table = Table(client_data, colWidths=[100, 320])
        client_table.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), "DejaVuSans", 10),
                    ("FONT", (0, 0), (0, -1), "DejaVuSans-Bold", 10),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("LINEBELOW", (0, -1), (-1, -1), 0.5, colors.lightgrey),
                ]
            )
        )
        client_table.wrapOn(pdf, width, height)
        client_table.drawOn(pdf, left_margin, current_y - (len(client_data) * line_height))
        current_y -= (len(client_data) * line_height) + section_spacing

        pdf.setFont("DejaVuSans-Bold", 12)
        pdf.drawString(left_margin, current_y, "Состав заказа:")
        current_y -= line_height

        items_data = [["№", "Наименование", "Кол-во", "Цена", "Сумма"]]
        for idx, item in enumerate(cart_products, 1):
            items_data.append(
                [
                    str(idx),
                    item["name"],
                    str(item["quantity"]),
                    format_price(item["price"]),
                    format_price(item["total"]),
                ]
            )

        row_height = 20
        start_row = 0
        while start_row < len(items_data):
            if current_y - (len(items_data) * row_height) < bottom_margin and start_row > 0:
                _draw_footer(pdf, left_margin, bottom_margin, privacy_date, order)
                pdf.showPage()
                current_y = top_margin
                pdf.setFont("DejaVuSans-Bold", 12)
                pdf.drawString(left_margin, current_y, "Состав заказа (продолжение):")
                current_y -= line_height

            available_space = current_y - bottom_margin
            max_rows = min(int(available_space / row_height), len(items_data) - start_row)
            if max_rows < 1:
                max_rows = 1
            end_row = start_row + max_rows
            part_table = Table(items_data[start_row:end_row], colWidths=[25, 250, 50, 80, 80])
            part_table.setStyle(
                TableStyle(
                    [
                        ("FONT", (0, 0), (-1, -1), "DejaVuSans", 9),
                        ("FONT", (0, 0), (-1, 0), "DejaVuSans-Bold", 9),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f5f5f5")),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 5),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ]
                )
            )
            part_height = (end_row - start_row) * row_height
            part_table.wrapOn(pdf, width, height)
            part_table.drawOn(pdf, left_margin, current_y - part_height)
            current_y -= part_height
            start_row = end_row

        pdf.setFont("DejaVuSans-Bold", 12)
        total_price_display = format_price(order.total_price) if order.total_price else "по запросу"
        pdf.drawString(right_margin - 180, current_y - 20, f"Итого: {total_price_display}")
        _draw_footer(pdf, left_margin, bottom_margin, privacy_date, order)
        pdf.save()
        return buffer.getvalue()
    except Exception:
        logger.exception("Ошибка генерации PDF")
        return None


def send_order_email_with_pdf(order: Request, pdf_content: bytes) -> bool:
    """Письмо уходит только если в .env явно задан ORDER_NOTIFICATION_EMAIL и SMTP."""
    try:
        notify_to = getattr(settings, "ORDER_NOTIFICATION_EMAIL", "") or ""
        if not notify_to:
            logger.info(
                "Заявка %s сохранена в БД без письма: ORDER_NOTIFICATION_EMAIL не задан",
                order.id,
            )
            return False
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            logger.info(
                "Заявка %s сохранена в БД без письма: SMTP (EMAIL_HOST_*) не настроен",
                order.id,
            )
            return False

        created_at = order.created_at.astimezone(NOVOSIBIRSK).strftime("%d.%m.%Y %H:%M")
        subject = f"Новая демо-заявка №{order.id} от {order.customer_name}"
        body = (
            f"Поступила демо-заявка №{order.id} от {created_at}.\n\n"
            f"Клиент: {order.customer_name}\n"
            f"Телефон: {order.customer_phone}\n"
            f"Email: {order.customer_email}\n\n"
            "Детали прикреплены в PDF. Это pet-проект, не боевой заказ.\n"
        )
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[notify_to],
            reply_to=[order.customer_email] if order.customer_email else None,
        )
        email.attach(f"order_{order.id}.pdf", pdf_content, "application/pdf")
        email.send(fail_silently=False)
        logger.info("Письмо по заявке %s отправлено на %s", order.id, notify_to)
        return True
    except Exception:
        logger.exception("Ошибка отправки письма по заказу %s", order.id)
        return False


def request_success(request: HttpRequest) -> HttpResponse:
    request_id = request.session.get("last_request_id")
    if not request_id:
        return redirect("mainPage")
    order = Request.objects.filter(id=request_id).first()
    if order is None:
        return redirect("mainPage")
    return render(request, "app/request_success.html", {"order": order})


def product_detail(request: HttpRequest, product_id: int) -> HttpResponse:
    product = get_object_or_404(
        Product.objects.prefetch_related("images", "diameters"),
        id=product_id,
    )
    return render(
        request,
        "app/products/product_detail.html",
        {"product": product, "characteristics": product.get_characteristics()},
    )


def _coerce_filter_values(field_name: str, values: list[str]) -> list:
    field = Product._meta.get_field(field_name)
    internal = field.get_internal_type()
    coerced = []
    for raw in values:
        if internal in {"IntegerField", "PositiveIntegerField", "BigIntegerField", "FloatField"}:
            try:
                number = float(str(raw).replace(",", "."))
                coerced.append(int(number) if internal != "FloatField" else number)
            except ValueError:
                continue
        else:
            coerced.append(raw)
    return coerced


def templateProducts(category: Category, request: HttpRequest) -> HttpResponse:
    products: QuerySet[Product] = Product.objects.filter(category=category).prefetch_related("images")
    characteristics: dict[str, str] = {}
    for product in products:
        for field, label in product.get_characteristics().items():
            characteristics.setdefault(field, label)

    selected: dict[str, list[str]] = {}
    query = Q()
    for key, values in request.GET.lists():
        if key not in characteristics or not values:
            continue
        selected[key] = values
        coerced = _coerce_filter_values(key, values)
        if coerced:
            query &= Q(**{f"{key}__in": coerced})

    filtered = products.filter(query) if selected else products

    def distinct_values(queryset: QuerySet[Product], field: str) -> list[str]:
        values = queryset.values_list(field, flat=True).distinct()
        return [str(value) for value in values if value not in (None, "")]

    all_characteristic_values = {field: distinct_values(products, field) for field in characteristics}
    if filtered.exists():
        available = {field: distinct_values(filtered, field) for field in characteristics}
    else:
        available = all_characteristic_values

    return render(
        request,
        "app/products/baseProducts.html",
        {
            "category": category,
            "products": filtered,
            "characteristics": characteristics,
            "selected_filters": selected,
            "characteristic_values": available,
            "all_characteristic_values": all_characteristic_values,
        },
    )


def weldingMachines(request: HttpRequest) -> HttpResponse:
    return render(request, "app/products/weldingMachines.html")


def hydraulicMachines(request: HttpRequest) -> HttpResponse:
    category = get_object_or_404(Category, name="Гидравлические сварочные аппараты")
    return templateProducts(category, request)


def mechanicalMachines(request: HttpRequest) -> HttpResponse:
    category = get_object_or_404(Category, name="Механические сварочные аппараты")
    return templateProducts(category, request)


def electrofusionMachines(request: HttpRequest) -> HttpResponse:
    category = get_object_or_404(Category, name="Электромуфтовые сварочные аппараты")
    return templateProducts(category, request)


def bellShapedMachines(request: HttpRequest) -> HttpResponse:
    category = get_object_or_404(Category, name="Раструбные сварочные аппараты")
    return templateProducts(category, request)


def componentsMachines(request: HttpRequest) -> HttpResponse:
    return render(request, "app/products/components.html")


def electorate(request: HttpRequest) -> HttpResponse:
    category = get_object_or_404(Category, name="Электроторцеватели")
    return templateProducts(category, request)


def electricHeater(request: HttpRequest) -> HttpResponse:
    category = get_object_or_404(Category, name="Электронагреватели")
    return templateProducts(category, request)


def earbuds(request: HttpRequest) -> HttpResponse:
    category = get_object_or_404(Category, name="Вкладыши")
    return templateProducts(category, request)


def scanner(request: HttpRequest) -> HttpResponse:
    category = get_object_or_404(Category, name="Сканер")
    return templateProducts(category, request)


def centralizersPipeWelding(request: HttpRequest) -> HttpResponse:
    category = get_object_or_404(Category, name="Центраторы для сварки труб")
    return templateProducts(category, request)


def additionalMachines(request: HttpRequest) -> HttpResponse:
    return render(request, "app/products/additional.html")


def automationUnit(request: HttpRequest) -> HttpResponse:
    category = get_object_or_404(Category, name="Блок автоматизации")
    return templateProducts(category, request)


def fitting(request: HttpRequest) -> HttpResponse:
    return render(request, "app/products/fitting.html")


def electrofusionFittings(request: HttpRequest) -> HttpResponse:
    category = get_object_or_404(Category, name="Электросварные фитинги")
    return templateProducts(category, request)


def castFittings(request: HttpRequest) -> HttpResponse:
    category = get_object_or_404(Category, name="Литые фитинги")
    return templateProducts(category, request)


def pipes(request: HttpRequest) -> HttpResponse:
    return render(request, "app/products/pipes.html")


def waterPipes(request: HttpRequest) -> HttpResponse:
    category = get_object_or_404(Category, name="Трубы ПНД водопроводные")
    return templateProducts(category, request)


def gasPipes(request: HttpRequest) -> HttpResponse:
    category = get_object_or_404(Category, name="Трубы ПНД для газа")
    return templateProducts(category, request)


def shutOffValves(request: HttpRequest) -> HttpResponse:
    return render(request, "app/products/shutOffValves.html")


def shutOffValvesFlange(request: HttpRequest) -> HttpResponse:
    category = get_object_or_404(Category, name="Фланец")
    return templateProducts(category, request)


def shutOffValvesFlangeAdapters(request: HttpRequest) -> HttpResponse:
    category = get_object_or_404(Category, name="Фланцевый адаптер")
    return templateProducts(category, request)


def rentalWeldingEquipment(request: HttpRequest) -> HttpResponse:
    return render(request, "app/service/rentalWeldingEquipment.html")


def repairWeldingEquipment(request: HttpRequest) -> HttpResponse:
    return render(request, "app/service/repairWeldingEquipment.html")


def pipelineInstallation(request: HttpRequest) -> HttpResponse:
    return render(request, "app/service/pipelineInstallation.html")
