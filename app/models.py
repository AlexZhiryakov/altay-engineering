from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название категории")
    description = models.TextField(verbose_name="Описание", max_length=1000, null=True, blank=True)
    attributes = models.ManyToManyField("Attribute", related_name="categories", verbose_name="Характеристики категории")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products", verbose_name="Категория")
    name = models.CharField(max_length=255, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена", null=True, blank=True)
    description = models.TextField(verbose_name="Описание", max_length=1000, null=True, blank=True)
    
    # Характеристики
    form = models.CharField(max_length=30, verbose_name="Форма", default='', blank=True)
    material = models.CharField(max_length=30, verbose_name="Материал", default='', blank=True)
    conditional_passage = models.IntegerField(verbose_name="Условный проход, Ду", null=True, blank=True)
    conditional_pressure = models.IntegerField(verbose_name="Условное давление, кгс/см2", null=True, blank=True)
    working_environment = models.CharField(max_length=200, verbose_name="Рабочая среда", default='', blank=True)
    working_temperature = models.CharField(max_length=75, verbose_name="Температура рабочей среды, °С", default='', blank=True)
    weight = models.CharField(max_length=15, verbose_name="Вес", default='', blank=True)

    shipment = models.CharField(max_length=30, verbose_name="Отгрузка", default='', blank=True)
    manufacturer = models.CharField(max_length=30, verbose_name="Производитель", default='', blank=True)
    pipe_diameter = models.IntegerField(verbose_name="Диаметр трубы, мм", null=True, blank=True)
    wall_thickness = models.FloatField(verbose_name="Толщина стенки, мм", null=True, blank=True)
    availability = models.CharField(max_length=15, verbose_name="Наличие", default='под заказ', blank=True)
    price_string = models.CharField(max_length=30, verbose_name="Строковая цена", default='по запросу', blank=True)

    menu_language = models.CharField(max_length=50, verbose_name="Язык меню", default='', blank=True)
    battery_life = models.CharField(verbose_name="Время автономной работы", max_length=255, default='', blank=True)
    food_type = models.CharField(verbose_name="Тип питания", max_length=255, default='', blank=True)
    display = models.CharField(verbose_name="Дисплей", max_length=255, default='', blank=True)
    memory_capacity = models.CharField(verbose_name="Объем памяти", max_length=255, default='', blank=True)
    data_storage = models.CharField(verbose_name="Накопитель данных", max_length=255, default='', blank=True)
    pressure_sensor_support = models.CharField(verbose_name="Поддержка датчиков давления", max_length=255, default='', blank=True)
    temperature_sensor_support = models.CharField(verbose_name="Поддержка датчиков температуры", max_length=255, default='', blank=True)
    length_sensor_wires = models.CharField(verbose_name="Длина проводов датчиков", max_length=255, default='', blank=True)
    operating_temp = models.CharField(max_length=50, verbose_name="Рабочая температура, °C", default='', blank=True)
    protection_class = models.CharField(max_length=50, verbose_name="Класс защиты", default='', blank=True)
    dimensions = models.CharField(max_length=255, verbose_name="Транспортировочные габариты, мм", default='', blank=True)
    packaging_type = models.CharField(max_length=255, verbose_name="Вид упаковки", default='', blank=True)
    output_current = models.CharField(max_length=50, verbose_name="Выходной ток, А", default='', blank=True)
    output_voltage = models.CharField(max_length=50, verbose_name="Выходное напряжение, В", default='', blank=True)
    operating_temperature = models.CharField(max_length=50, verbose_name="Рабочая температура, °C", default='', blank=True)

    welding_range = models.CharField(max_length=100, verbose_name="Диапазон сварки, мм", default='', blank=True)
    drive_type = models.CharField(max_length=255, verbose_name="Привод", default='', blank=True)
    earbuds = models.CharField(max_length=100, verbose_name="Вкладыши, мм", default='', blank=True) 
    clamp_count = models.IntegerField(verbose_name="Количество зажимов", null=True, blank=True)
    
    # Доп поле для раструбных сварочных аппаратов
    heating_time = models.IntegerField(verbose_name="Время нагрева, мин", null=True, blank=True)

    # Доп поля для электромуфтовых сварочных аппаратов
    logging_function = models.CharField(verbose_name="Функция протоколирования", max_length=255, default='', blank=True)
    protocol_export = models.CharField(verbose_name="Выгрузка протоколов", max_length=255, default='', blank=True)
    data_input = models.CharField(max_length=255, verbose_name="Ввод данных", default='', blank=True)
    welding_time = models.CharField(max_length=50, verbose_name="Время сварки, сек", default='', blank=True)
    protocol_count = models.IntegerField(verbose_name="Количество протоколов в памяти, шт", null=True, blank=True)
    power = models.IntegerField(verbose_name="Мощность, Вт", null=True, blank=True)
    current_consumption = models.IntegerField(verbose_name="Потребляемый ток, А", null=True, blank=True)
    trimmer_power = models.IntegerField(verbose_name="Мощность торцевателя, Вт", null=True, blank=True)
    heater_power = models.IntegerField(verbose_name="Мощность нагревателя, Вт", null=True, blank=True)
    net_weight = models.CharField(max_length=50, verbose_name="Масса нетто/брутто, кг", default='', blank=True)

    hydraulic_power = models.IntegerField(verbose_name="Мощность двигателя гидростанции, Вт", null=True, blank=True)
    total_power_consumption = models.IntegerField(verbose_name="Общая потребляемая мощность, Вт", null=True, blank=True)
    max_pressure = models.IntegerField(verbose_name="Максимальное давление, бар", null=True, blank=True)
    cylinder_area = models.FloatField(verbose_name="Площадь сечения цилиндров, см²", null=True, blank=True)
    warranty = models.IntegerField(verbose_name="Гарантия, лет", null=True, blank=True)
    supply_voltage = models.CharField(max_length=50, verbose_name="Напряжение питания, В/Гц", default='', blank=True)


    def get_characteristics(self):
        """Возвращает словарь с характеристиками товара, исключая пустые значения."""
        characteristics = {}
        fields = [
            ("form", "Форма"),
            ("material", "Материал"),
            ("conditional_passage", "Условный проход, Ду"),
            ("conditional_pressure", "Условное давление, кгс/см2"),
            ("working_environment", "Рабочая среда"),
            ("working_temperature", "Температура рабочей среды, °С"),
            ("weight", "Вес"),
            ("shipment", "Отгрузка"),
            ("manufacturer", "Производитель"),
            ("pipe_diameter", "Диаметр трубы, мм"),
            ("wall_thickness", "Толщина стенки, мм"),
            ("availability", "Наличие"),
            ("menu_language", "Язык меню"),
            ("battery_life", "Время автономной работы"),
            ("food_type", "Тип питания"),
            ("display", "Дисплей"),
            ("memory_capacity", "Объем памяти"),
            ("data_storage", "Накопитель данных"),
            ("pressure_sensor_support", "Поддержка датчиков давления"),
            ("temperature_sensor_support", "Поддержка датчиков температуры"),
            ("length_sensor_wires", "Длина проводов датчиков"),
            ("operating_temp", "Рабочая температура, °C"),
            ("protection_class", "Класс защиты"),
            ("dimensions", "Транспортировочные габариты, мм"),
            ("packaging_type", "Вид упаковки"),
            ("output_current", "Выходной ток, А"),
            ("output_voltage", "Выходное напряжение, В"),
            ("operating_temperature", "Рабочая температура, °C"),
            ("welding_range", "Диапазон сварки, мм"),
            ("earbuds", "Вкладыши, мм"),
            ("clamp_count", "Количество зажимов"),
            ("heating_time", "Время нагрева, мин"),
            ("logging_function", "Функция протоколирования"),
            ("protocol_export", "Выгрузка протоколов"),
            ("data_input", "Ввод данных"),
            ("welding_time", "Время сварки, сек"),
            ("protocol_count", "Количество протоколов в памяти, шт"),
            ("power", "Мощность, Вт"),
            ("current_consumption", "Потребляемый ток, А"),
            ("trimmer_power", "Мощность торцевателя, Вт"),
            ("heater_power", "Мощность нагревателя, Вт"),
            ("net_weight", "Масса нетто/брутто, кг"),
            ("hydraulic_power", "Мощность двигателя гидростанции, Вт"),
            ("total_power_consumption", "Общая потребляемая мощность, Вт"),
            ("max_pressure", "Максимальное давление, бар"),
            ("cylinder_area", "Площадь сечения цилиндров, см²"),
            ("warranty", "Гарантия, лет"),
            ("supply_voltage", "Напряжение питания, В/Гц"),
        ]

        for field, label in fields:
            value = getattr(self, field)
            if value not in (None, '', []):
                characteristics[label] = value

        return characteristics


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class FittingDiameter(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="diameters", verbose_name="Товар")
    diameter = models.CharField(max_length=50, verbose_name="Диаметр")

    def __str__(self):
        return f"{self.product.name} - {self.diameter}"

    class Meta:
        verbose_name = "Диаметр фитинга"
        verbose_name_plural = "Диаметры фитингов"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images", verbose_name="Товар")
    image = models.ImageField(upload_to="products/", verbose_name="Изображение")

    def __str__(self):
        return f"Изображение для {self.product.name}"
    
class Attribute(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название характеристики")

    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="attribute_values")
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=255, verbose_name="Значение характеристики")

    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}: {self.value}"
    

class Request(models.Model):
    """Модель заявки от клиента"""
    customer_name = models.CharField(max_length=100, verbose_name="ФИО клиента")
    customer_phone = models.CharField(max_length=20, verbose_name="Телефон клиента")
    customer_email = models.EmailField(verbose_name="Email клиента", null=True, blank=True)
    comment = models.TextField(verbose_name="Комментарий к заявке", max_length=1000, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    is_processed = models.BooleanField(default=False, verbose_name="Обработана")
    
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Общая стоимость",
        null=True,
        blank=True
    )
    
    has_price_request_items = models.BooleanField(
        default=False,
        verbose_name="Есть товары с ценой по запросу"
    )

    privacy_policy_accepted = models.BooleanField(
        verbose_name="Согласие с политикой конфиденциальности",
        default=False
    )
    
    privacy_policy_accepted_at = models.DateTimeField(
        verbose_name="Дата согласия",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заявка #{self.id} от {self.created_at.strftime('%d.%m.%Y')}"


class RequestItem(models.Model):
    """Позиции в заявке"""
    request = models.ForeignKey(
        Request,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Заявка"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='request_items',
        verbose_name="Товар"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Количество"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена на момент заявки",
        null=True,
        blank=True
    )
    
    product_name = models.CharField(max_length=255, verbose_name="Название товара")
    product_description = models.TextField(verbose_name="Описание товара", max_length=1000, null=True, blank=True)

    class Meta:
        verbose_name = "Позиция заявки"
        verbose_name_plural = "Позиции заявки"

    def __str__(self):
        return f"{self.product_name} (x{self.quantity})"

    @property
    def total_price(self):
        return self.price * self.quantity if self.price else None

    def save(self, *args, **kwargs):
        # Сохраняем актуальные данные о товаре
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_description:
            self.product_description = self.product.description
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)