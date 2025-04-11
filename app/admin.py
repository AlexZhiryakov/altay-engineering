from django.contrib import admin
from .models import Category, Product, ProductImage, FittingDiameter, Attribute, ProductAttributeValue, Request, RequestItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

class ProductImageInline(admin.TabularInline):  
    model = ProductImage

class FittingDiameterInline(admin.TabularInline):
    model = FittingDiameter
    extra = 1  # Количество пустых форм для добавления диаметров

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "category")
    list_filter = ("category",)
    search_fields = ("name", "description")
    inlines = [ProductImageInline, FittingDiameterInline]  # Добавляем inline для изображений и диаметров

admin.site.register(ProductImage)

@admin.register(FittingDiameter)
class FittingDiameterAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "diameter")
    search_fields = ("product__name", "diameter")

@admin.register(Attribute)
class Attribute(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(ProductAttributeValue)
class ProductAttributeValue(admin.ModelAdmin):
    list_display = ("product", "attribute", "value")
    search_fields = ("product",)

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_phone', 'created_at', 'is_processed')
    list_filter = ('is_processed', 'created_at')
    search_fields = ('customer_name', 'customer_phone')

@admin.register(RequestItem)
class RequestItemAdmin(admin.ModelAdmin):
    list_display = ('request', 'product_name', 'quantity', 'price')
    search_fields = ('product_name', 'request__customer_name')