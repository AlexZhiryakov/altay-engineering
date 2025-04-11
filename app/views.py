from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.http import FileResponse, HttpResponseNotFound, JsonResponse
from .models import Category, Product, ProductAttributeValue
import os
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Request, RequestItem
from django.contrib.auth.decorators import login_required
from app.models import Request
from django.db.models import Q
from django.utils import timezone
import pytz
from io import BytesIO
from django.core.mail import EmailMessage
import logging
from django.conf import settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

logger = logging.getLogger(__name__)

# Регистрация шрифта (вызывается один раз при старте приложения)
def register_fonts():
    try:
        font_path = os.path.join(settings.BASE_DIR, "static", "fonts", "DejaVuSans.ttf")
        bold_font_path = os.path.join(settings.BASE_DIR, "static", "fonts", "DejaVuSans-Bold.ttf")
        
        # Регистрируем обычное и жирное начертание
        pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
        
        # Если есть отдельный файл для жирного начертания
        if os.path.exists(bold_font_path):
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', bold_font_path))
        else:
            # Если нет отдельного файла, используем обычный шрифт с установкой bold
            from reportlab.lib.fonts import addMapping
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', font_path))
            addMapping('DejaVuSans', 0, 1, 'DejaVuSans-Bold')  # normal, bold, italic
            
        logger.info("Шрифты DejaVuSans успешно зарегистрированы")
    except Exception as e:
        logger.error(f"Ошибка регистрации шрифтов: {e}")
        # Fallback на стандартные шрифты
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'Arial'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'Arial-Bold'))

# Форматирование итоговой стоимости
def format_price(value):
    if value is None:
        return "по запросу"
    try:
        return f"{int(value):,}".replace(",", " ") + " ₽"
    except (ValueError, TypeError):
        return str(value)

# Главная страница
def mainPage(request):
    return render(request, 'app/mainPage.html')

# Загрузка файла
def download_file(request):
    file_path = os.path.join(settings.MEDIA_ROOT, 'Карточка_ООО_Алтаи-Инжиниринг.pdf')
    if not os.path.exists(file_path):
        return HttpResponseNotFound("Файл не найден")
    return FileResponse(open(file_path, 'rb'), as_attachment=True)


# Вкладки на сайте

# Политика конфиденциальности

def privacyPolicy(request):
    return render(request, 'app/privacyPolicy.html')

# Компания

# О компании
def aboutCompany(request):
    return render(request, 'app/company/aboutCompany.html')

# Реквизиты
def companyDetails(request):
    return render(request, 'app/company/companyDetails.html')

# Корзина
def shoppingCart(request):
    cart = request.session.get('cart', {})
    cart_items = {}
    total_cart_price = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            cart_items[product] = quantity  # Добавляем товар независимо от наличия цены
            
            # Считаем общую стоимость только для товаров с ценой
            if product.price is not None:
                total_cart_price += product.price * quantity
        except Product.DoesNotExist:
            continue
    
    context = {
        'cart_items': cart_items,  # Все товары, включая те, у которых нет цены
        'total_cart_price': total_cart_price if cart_items else None
    }
    return render(request, 'app/shoppingCart.html', context)

# Добавление в корзину
def add_to_cart(request):
    product_id = request.GET.get("product_id")
    if not product_id:
        return JsonResponse({"error": "Нет product_id"}, status=400)

    cart = request.session.get("cart", {})

    if product_id in cart:
        del cart[product_id]  # Удаляем товар, если он уже был добавлен
        in_cart = False
    else:
        cart[product_id] = 1  # Добавляем товар в корзину
        in_cart = True

    request.session["cart"] = cart  # Сохраняем обновленную корзину
    request.session.modified = True

    return JsonResponse({"in_cart": in_cart})

# Обработка количества товаров
def update_cart(request):
    product_id = request.GET.get("product_id")
    action = request.GET.get("action")
    quantity = request.GET.get("quantity", 1)

    if not product_id:
        return JsonResponse({"error": "Некорректные данные"}, status=400)

    cart = request.session.get("cart", {})
    product = get_object_or_404(Product, id=int(product_id))

    if action == "set":
        if int(quantity) == 0:
            if product_id in cart:
                del cart[product_id]
        else:
            cart[product_id] = max(1, int(quantity))
    elif action == "remove":
        if product_id in cart:
            del cart[product_id]

    request.session["cart"] = cart
    request.session.modified = True

    # Пересчитываем общую стоимость только для товаров с ценой
    total_cart_price = 0
    for pid, qty in cart.items():
        p = Product.objects.get(id=int(pid))
        if p.price is not None:
            total_cart_price += p.price * qty

    if product_id not in cart:
        return JsonResponse({
            "success": True,
            "quantity": 0,
            "total_price": 0,
            "total_cart_price": total_cart_price
        })

    total_price = product.price * cart[product_id] if product.price is not None else None

    return JsonResponse({
        "success": True,
        "quantity": cart[product_id],
        "total_price": total_price,
        "total_cart_price": total_cart_price
    })

# Оформление заказа

def placeOrder(request):
    if request.method == 'POST':
        logger.info("Начало обработки заказа")
        
        try:
            # Валидация данных формы
            name = request.POST.get('name', '').strip()
            phone = request.POST.get('phone', '').strip()
            email = request.POST.get('email', '').strip().lower()
            comment = request.POST.get('comment', '').strip()
            privacy_policy = request.POST.get('privacy_policy') == 'on'
            
            if not all([name, phone, email]):
                messages.error(request, 'Пожалуйста, заполните все обязательные поля')
                return redirect('place-order')
                
            if not privacy_policy:
                messages.error(request, 'Необходимо согласие с политикой конфиденциальности')
                return redirect('place-order')
                
            cart = request.session.get('cart', {})
            if not cart:
                messages.error(request, 'Ваша корзина пуста')
                return redirect('shopping-cart')
            
            # Создаем заявку
            novosibirsk_tz = pytz.timezone('Asia/Novosibirsk')
            current_time = timezone.now().astimezone(novosibirsk_tz)
            
            request_obj = Request.objects.create(
                customer_name=name,
                customer_phone=phone,
                customer_email=email,
                comment=comment,
                is_processed=False,
                privacy_policy_accepted=True,
                privacy_policy_accepted_at=current_time,
                created_at=current_time
            )
            
            # Обрабатываем товары
            total_price = 0
            has_price_request = False
            cart_products = []
            
            for product_id, quantity in cart.items():
                try:
                    product = Product.objects.get(id=product_id)
                    RequestItem.objects.create(
                        request=request_obj,
                        product=product,
                        quantity=quantity,
                        price=product.price,
                        product_name=product.name,
                        product_description=product.description
                    )
                    
                    item_total = product.price * quantity if product.price else 0
                    cart_products.append({
                        'name': product.name,
                        'quantity': quantity,
                        'price': product.price if product.price else 'по запросу',
                        'total': item_total if product.price else 'по запросу'
                    })
                    
                    if product.price:
                        total_price += item_total
                    else:
                        has_price_request = True
                        
                except Product.DoesNotExist:
                    continue
            
            # Обновляем заказ
            request_obj.total_price = total_price if total_price > 0 else None
            request_obj.has_price_request_items = has_price_request
            request_obj.save()
            
            # Пытаемся отправить письмо, но не блокируем процесс
            try:
                pdf_content = generate_order_pdf(request_obj, cart_products)
                if pdf_content:
                    # Запускаем отправку в отдельном потоке, чтобы не блокировать ответ
                    import threading
                    threading.Thread(
                        target=send_order_email_with_pdf,
                        args=(request_obj, cart_products, pdf_content),
                        daemon=True
                    ).start()
            except Exception as e:
                logger.error(f"Ошибка при генерации PDF: {str(e)}")
            
            # Очищаем корзину
            request.session['cart'] = {}
            request.session['last_request_id'] = request_obj.id
            request.session.modified = True
            
            return redirect('request-success')
            
        except Exception as e:
            logger.error(f"Ошибка при создании заказа: {str(e)}", exc_info=True)
            messages.error(request, 'Произошла ошибка при оформлении заказа. Пожалуйста, попробуйте позже.')
            return redirect('place-order')
    
    # GET запрос - отображение формы
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, 'Ваша корзина пуста')
        return redirect('shopping-cart')
    
    cart_items = {}
    total_cart_price = 0
    has_price_request_items = False
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            cart_items[product] = quantity
            
            if product.price is not None:
                total_cart_price += product.price * quantity
            else:
                has_price_request_items = True
        except Product.DoesNotExist:
            continue
    
    context = {
        'cart_items': cart_items,
        'total_cart_price': total_cart_price if cart_items else None,
        'has_price_request_items': has_price_request_items
    }
    return render(request, 'app/placeOrder.html', context)

def _draw_footer(canvas, left_margin, y_pos, privacy_date, order):
    """Вспомогательная функция для отрисовки футера"""
    canvas.setFont("DejaVuSans", 8)
    canvas.drawString(left_margin, y_pos, "Согласие с политикой конфиденциальности: " + 
                     ("Да" if order.privacy_policy_accepted else "Нет"))
    canvas.drawString(left_margin, y_pos - 15, f"Дата согласия: {privacy_date}")
    canvas.drawString(left_margin, y_pos - 30, "Документ сформирован автоматически")

def generate_order_pdf(order, cart_products):
    try:
        # Регистрируем шрифты
        register_fonts()
        
        # Инициализируем временные переменные
        novosibirsk_tz = pytz.timezone('Asia/Novosibirsk')
        created_at = order.created_at.astimezone(novosibirsk_tz).strftime('%d.%m.%Y %H:%M')
        privacy_date = order.privacy_policy_accepted_at.astimezone(novosibirsk_tz).strftime('%d.%m.%Y %H:%M')
        
        # Создаем буфер для PDF
        buffer = BytesIO()
        
        # Создаем canvas (холст) для PDF
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Устанавливаем отступы и параметры
        left_margin = 50
        right_margin = width - 50
        top_margin = height - 50
        bottom_margin = 100  # Место для футера
        line_height = 20
        section_spacing = 30
        
        # 1. Заголовок документа (первая страница)
        c.setFont("DejaVuSans-Bold", 18)
        c.drawString(left_margin, top_margin, "Altay Engineering")
        
        c.setFont("DejaVuSans", 10)
        c.drawString(left_margin, top_margin - line_height, f"Дата: {created_at}")
        
        # 2. Информация о заказе
        current_y = top_margin - line_height * 2 - 10
        
        c.setFont("DejaVuSans-Bold", 14)
        c.drawString(left_margin, current_y, f"Заказ №{order.id}")
        
        # 3. Информация о клиенте
        current_y -= line_height + 10
        
        c.setFont("DejaVuSans-Bold", 12)
        c.drawString(left_margin, current_y, "Информация о клиенте:")
        current_y -= line_height
        
        client_data = [
            ["ФИО:", order.customer_name],
            ["Телефон:", order.customer_phone],
            ["Email:", order.customer_email],
            ["Комментарий:", order.comment or "-"]
        ]
        
        client_table = Table(client_data, colWidths=[100, 320])
        client_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'DejaVuSans', 10),
            ('FONT', (0, 0), (0, -1), 'DejaVuSans-Bold', 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.lightgrey),
        ]))
        client_table.wrapOn(c, width, height)
        client_table.drawOn(c, left_margin, current_y - (len(client_data) * line_height))
        current_y -= (len(client_data) * line_height) + section_spacing
        
        # 4. Состав заказа (может занимать несколько страниц)
        c.setFont("DejaVuSans-Bold", 12)
        c.drawString(left_margin, current_y, "Состав заказа:")
        current_y -= line_height
        
        # Разбиваем товары на части для пагинации
        items_per_page = 25  # Количество товаров на странице
        items_data = [["№", "Наименование", "Кол-во", "Цена", "Сумма"]]
        
        for idx, item in enumerate(cart_products, 1):
            items_data.append([
                str(idx),
                item['name'],
                str(item['quantity']),
                format_price(item['price']),
                format_price(item['total'])
            ])
        
        # Вычисляем высоту таблицы
        row_height = 20
        header_height = 25
        table_height = len(items_data) * row_height
        
        # Рисуем таблицу по частям
        start_row = 0
        while start_row < len(items_data):
            # Проверяем, нужно ли создавать новую страницу
            if current_y - table_height < bottom_margin:
                # Добавляем футер на текущую страницу
                _draw_footer(c, left_margin, bottom_margin, privacy_date, order)
                
                # Создаем новую страницу
                c.showPage()
                current_y = top_margin
                
                # Заголовок на новой странице
                c.setFont("DejaVuSans-Bold", 12)
                c.drawString(left_margin, current_y, "Состав заказа (продолжение):")
                current_y -= line_height
            
            # Определяем сколько строк поместится на текущей странице
            available_space = current_y - bottom_margin
            max_rows = min(int(available_space / row_height), len(items_data) - start_row)
            end_row = start_row + max_rows
            
            # Создаем таблицу для текущей части
            part_table = Table(items_data[start_row:end_row], colWidths=[25, 250, 50, 80, 80])
            part_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'DejaVuSans', 9),
                ('FONT', (0, 0), (-1, 0), 'DejaVuSans-Bold', 9),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f5f5f5')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            
            # Рисуем часть таблицы
            part_height = (end_row - start_row) * row_height
            part_table.wrapOn(c, width, height)
            part_table.drawOn(c, left_margin, current_y - part_height)
            
            # Обновляем позицию и счетчик строк
            current_y -= part_height
            start_row = end_row
        
        # 5. Итого (на последней странице)
        c.setFont("DejaVuSans-Bold", 12)
        total_price_display = format_price(order.total_price) if order.total_price else "по запросу"
        c.drawString(right_margin - 180, current_y - 20, f"Итого: {total_price_display}")
        
        # 6. Футер на последней странице
        _draw_footer(c, left_margin, bottom_margin, privacy_date, order)
        
        # Сохраняем PDF
        c.save()
        return buffer.getvalue()

    except Exception as e:
        logger.error(f"Ошибка генерации PDF: {str(e)}")
        return None
    
def send_order_email_with_pdf(order, cart_products, pdf_content):
    """Отправка письма с прикрепленным PDF"""
    try:
        # Проверяем, что письма включены в настройках
        if not hasattr(settings, 'EMAIL_HOST_USER') or not settings.EMAIL_HOST_USER:
            logger.warning("Отправка почты отключена (не настроен EMAIL_HOST_USER)")
            return False
        
        novosibirsk_tz = pytz.timezone('Asia/Novosibirsk')
        created_at = order.created_at.astimezone(novosibirsk_tz).strftime('%d.%m.%Y %H:%M')
        
        subject = f'Новый заказ №{order.id} от {order.customer_name}'
        
        email_body = f"""
Поступил новый заказ №{order.id} от {created_at}.

Клиент: {order.customer_name}
Телефон: {order.customer_phone}
Email: {order.customer_email}

Детали заказа прикреплены в PDF-файле.
"""
        try:
            email = EmailMessage(
                subject=subject,
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.DEFAULT_FROM_EMAIL],  # Отправляем на тот же адрес
                reply_to=[order.customer_email]
            )
            
            if pdf_content:
                email.attach(
                    f'order_{order.id}.pdf',
                    pdf_content,
                    'application/pdf'
                )
            
            # Отправляем с таймаутом 10 секунд
            email.timeout = 10
            email.send(fail_silently=False)
            logger.info(f"Письмо с заказом {order.id} успешно отправлено")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки письма: {str(e)}", exc_info=True)
            return False
            
    except Exception as e:
        logger.error(f"Ошибка в send_order_email_with_pdf: {str(e)}", exc_info=True)
        return False

@login_required
def request_success(request):
    request_id = request.session.get('last_request_id')
    if not request_id:
        logger.warning("Попытка доступа к request-success без ID заказа")
        return redirect('mainPage')

    try:
        request_obj = Request.objects.get(id=request_id)
        context = {'request': request_obj}
        return render(request, 'app/request_success.html', context)
    except Request.DoesNotExist:
        logger.error(f"Заказ с ID {request_id} не найден в БД")
        return redirect('mainPage')


# Детали товаров

def product_detail(request, product_id):
    # Получаем товар по ID
    product = get_object_or_404(Product, id=product_id)

    characteristics = {
    "welding_range": "Диапазон сварки",
    "drive_type": "Привод",
    "clamp_count": "Количество зажимов",
    "power_voltage": "Напряжение питания",
    "heater_power": "Мощность нагревателя, Вт",
    "trimmer_power": "Мощность торцевателя, Вт",
    "hydraulic_power": "Мощность двигателя гидростанции, Вт",
    "total_power_consumption": "Общая потребляемая мощность, Вт",
    "max_pressure": "Максимальное давление, бар",
    "cylinder_area": "Площадь сечения цилиндров, см²",
    "operating_temp": "Рабочая температура, °C",
    "net_weight": "Масса нетто/брутто, кг",
    "dimensions": "Транспортировочные габариты, мм",
    "warranty": "Гарантия, лет",
    "packaging_type": "Вид упаковки",
    "shipment": "Отгрузка",
    "manufacturer": "Производитель",
    "pipe_diameter": "Диаметр трубы, мм",
    "wall_thickness": "Толщина стенки, мм",
    "availability": "Наличие",
    "material": "Материал",
    "conditional_passage": "Условный проход, Ду",
    "conditional_pressure": "Условное давление, Ду",
    "working_environment": "Рабочая среда",
    "working_temperature": "Температура рабочей среды, °С",
    "weight": "Вес"
    }

    context = {
        "product": product,
        'characteristics': product.get_characteristics(),
    }   

    return render(request, 'app/products/product_detail.html', context)


# Каталог

def category_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)

    # Получаем характеристики, которые относятся к данной категории
    attributes = category.attributes.all()

    # Собираем уникальные значения характеристик
    attribute_values = {
        attr.name: ProductAttributeValue.objects.filter(
            attribute=attr, product__category=category
        ).values_list("value", flat=True).distinct()
        for attr in attributes
    }

    # Фильтрация товаров
    filters = {}
    for attr in attributes:
        value = request.GET.get(attr.name)
        if value:
            filters[f'attribute_values__attribute'] = attr
            filters[f'attribute_values__value'] = value

    if filters:
        products = products.filter(**filters).distinct()

    return render(request, "products/baseProducts.html", {
        "category": category,
        "products": products,
        "attributes": attributes,
        "attribute_values": attribute_values
    })


# Шаблон вывода категории товаров
def templateProducts(category, request):
    products = Product.objects.filter(category=category)

    # Получаем все характеристики товаров
    all_characteristics = {}
    for product in products:
        for field, label in product.get_characteristics().items():
            if field not in all_characteristics:
                all_characteristics[field] = label

    # Фильтрация по выбранным характеристикам
    filters = {}
    filter_queries = Q()
    
    for key, values in request.GET.lists():
        if key in all_characteristics:
            normalized_values = []
            for v in values:
                # Заменяем запятые на точки ТОЛЬКО для площади сечения
                if key == 'cross_sectional_area':
                    normalized = v.replace(",", ".")
                else:
                    normalized = v
                normalized_values.append(normalized)
            
            filters[key] = normalized_values
            
            # Для габаритов используем точное сравнение
            if 'х' in values[0]:  # Если значение содержит символы габаритов
                filter_queries &= Q(**{f"{key}__in": normalized_values})
            else:
                filter_queries &= Q(**{f"{key}__in": normalized_values})

    # Получаем все возможные значения характеристик ДО фильтрации
    all_characteristic_values = {}
    for field in all_characteristics:
        values = products.values_list(field, flat=True).distinct()
        all_characteristic_values[field] = [str(v) if v is not None else "" for v in values]

    # Применяем фильтрацию
    filtered_products = products.filter(filter_queries) if filters else products

    # Получаем доступные значения характеристик ПОСЛЕ фильтрации
    available_characteristic_values = {}
    for field in all_characteristics:
        if filtered_products.exists():  # Если есть отфильтрованные товары
            values = filtered_products.values_list(field, flat=True).distinct()
            available_characteristic_values[field] = [str(v) if v is not None else "" for v in values]
        else:
            # Если товаров нет, показываем все возможные значения
            available_characteristic_values[field] = all_characteristic_values[field]

    return render(request, 'app/products/baseProducts.html', {
        'category': category,
        'products': filtered_products,
        'characteristics': all_characteristics,
        'selected_filters': filters,
        'characteristic_values': available_characteristic_values,
        'all_characteristic_values': all_characteristic_values,
    })


# Сварочные аппараты
def weldingMachines(request):
    return render(request, 'app/products/weldingMachines.html')

# Гидравлические сварочные аппараты  
def hydraulicMachines(request):
    category = get_object_or_404(Category, name="Гидравлические сварочные аппараты")
    return templateProducts(category, request)

# Механические
def mechanicalMachines(request):
    category = get_object_or_404(Category, name="Механические сварочные аппараты")
    return templateProducts(category, request)

# Электромуфтовые
def electrofusionMachines(request):
    category = get_object_or_404(Category, name="Электромуфтовые сварочные аппараты")
    return templateProducts(category, request)

# Раструбные
def bellShapedMachines(request):
    category = get_object_or_404(Category, name="Раструбные сварочные аппараты")
    return templateProducts(category, request)


# Комплектующие
def componentsMachines(request):
    return render(request, 'app/products/components.html')

# Электорцеватель
def electorate(request):
    category = get_object_or_404(Category, name="Электроторцеватели")
    return templateProducts(category, request)

# Электронагреватель
def electricHeater(request):
    category = get_object_or_404(Category, name="Электронагреватели")
    return templateProducts(category, request)

# Вкладыши
def earbuds(request):
    category = get_object_or_404(Category, name="Вкладыши")
    return templateProducts(category, request)

# Сканер
def scanner(request):
    category = get_object_or_404(Category, name="Сканер")
    return templateProducts(category, request)

# Центраторы для сварки труб
def centralizersPipeWelding(request):
    category = get_object_or_404(Category, name="Центраторы для сварки труб")
    return templateProducts(category, request)


# Дополнительные
def additionalMachines(request):
    return render(request, 'app/products/additional.html')

# Блок автоматизации
def automationUnit(request):
    category = get_object_or_404(Category, name="Блок автоматизации")
    return templateProducts(category, request)



# Фитинги
def fitting(request):
    return render(request, 'app/products/fitting.html')

# Электросварные фитинги
def electrofusionFittings(request):
    category = get_object_or_404(Category, name="Электросварные фитинги")
    return templateProducts(category, request)

# Литые фитинги
def castFittings(request):
    category = get_object_or_404(Category, name="Литые фитинги")
    return templateProducts(category, request)


# Трубы ПНД
def pipes(request):
    return render(request, 'app/products/pipes.html')

# Трубы ПНД водопроводные
def waterPipes(request):
    category = get_object_or_404(Category, name="Трубы ПНД водопроводные")
    return templateProducts(category, request)

# Трубы ПНД для газа
def gasPipes(request):
    category = get_object_or_404(Category, name="Трубы ПНД для газа")
    return templateProducts(category, request)


# Запорная арматура
def shutOffValves(request):
    return render(request, 'app/products/shutOffValves.html')

# Фланец
def shutOffValvesFlange(request):
    category = get_object_or_404(Category, name="Фланец")
    return templateProducts(category, request)

# Фланцевый адаптер
def shutOffValvesFlangeAdapters(request):
    category = get_object_or_404(Category, name="Фланцевый адаптер")
    return templateProducts(category, request)


# Услуги

# Аренда
def rentalWeldingEquipment(request):
    return render(request, 'app/service/rentalWeldingEquipment.html')

# Ремонт
def repairWeldingEquipment(request):
    return render(request, 'app/service/repairWeldingEquipment.html')

# Монтаж трубопровода
def pipelineInstallation(request):
    return render(request, 'app/service/pipelineInstallation.html')