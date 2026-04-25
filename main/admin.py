from django.contrib import admin
from .models import ProductImage, ProductColor, Category, Product, Color, Banner

# Register your models here.

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price']
    list_filter = ['category']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductColorInline]


@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ['product', 'color', 'stock']
    list_filter = ['color', 'product']
    inlines = [ProductImageInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'hex_code']


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')