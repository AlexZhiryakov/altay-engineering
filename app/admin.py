from django.contrib import admin

from .models import (
    Attribute,
    Category,
    FittingDiameter,
    Product,
    ProductAttributeValue,
    ProductImage,
    Request,
    RequestItem,
)

admin.site.site_header = "AlexZhiryakov · демо"
admin.site.site_title = "AlexZhiryakov"
admin.site.index_title = "Управление демо-каталогом"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


class ProductImageInline(admin.TabularInline):
    model = ProductImage


class FittingDiameterInline(admin.TabularInline):
    model = FittingDiameter
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "category")
    list_filter = ("category",)
    search_fields = ("name", "description")
    inlines = [ProductImageInline, FittingDiameterInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("id", "product")


@admin.register(FittingDiameter)
class FittingDiameterAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "diameter")
    search_fields = ("product__name", "diameter")


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ("product", "attribute", "value")
    search_fields = ("product__name", "value")


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "customer_phone", "created_at", "is_processed")
    list_filter = ("is_processed", "created_at")
    search_fields = ("customer_name", "customer_phone", "customer_email")


@admin.register(RequestItem)
class RequestItemAdmin(admin.ModelAdmin):
    list_display = ("request", "product_name", "quantity", "price")
    search_fields = ("product_name", "request__customer_name")
