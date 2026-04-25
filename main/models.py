from django.db import models
from django.utils.text import slugify

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
      if not self.slug:
          self.slug = slugify(self.name)
      super().save(*args, **kwargs)

    
    def __str__(self):
        return self.name
    

class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    main_image = models.ImageField(upload_to='products/main/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    
    def __str__(self):
        return self.name
    

class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    hex_code = models.CharField(max_length=7)

    def __str__(self):
        return self.name
    

class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_variants')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='color_variants')
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product', 'color')
        ordering = ['id']

    def __str__(self):
        return f"{self.color.name} ({self.product.name} - {self.stock})"
    

class ProductImage(models.Model):
    variant = models.ForeignKey(ProductColor, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Image for {self.variant}"
    

class Banner(models.Model):
    title = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='slides/')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title or f"Slide {self.id}"