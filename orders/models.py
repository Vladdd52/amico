from django.db import models
from main.models import ProductColor

class Order(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая сумма", default=0)
    
    STATUS_CHOICES = (
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('canceled', 'Отменен'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлен")

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"Заказ #{self.id} - {self.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductColor, on_delete=models.SET_NULL, null=True, related_name='order_items', verbose_name="Товар")
    product_name = models.CharField(max_length=200, verbose_name="Название товара", default="Товар")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена при заказе")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

    def __str__(self):
        return f"Товар {self.id} в заказе {self.order.id}"

    def get_cost(self):
        return self.price * self.quantity
