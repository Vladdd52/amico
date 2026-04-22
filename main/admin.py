from django.contrib import admin
from main.models import ProductImage, ProductColor

# Register your models here.

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]