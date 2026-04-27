from decimal import Decimal
from copy import deepcopy
from django.conf import settings
from main.models import ProductColor

class Cart:
    def __init__(self, request):
        """Инициализация корзины."""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product_variant, quantity=1, update_quantity=False):
        """Добавление товара (варианта цвета) в корзину или обновление его количества."""
        variant_id = str(product_variant.id)
        
        if variant_id not in self.cart:
            price = product_variant.product.discount_price if product_variant.product.discount_price else product_variant.product.price
            self.cart[variant_id] = {'quantity': 0, 'price': str(price)}

        if update_quantity:
            self.cart[variant_id]['quantity'] = quantity
        else:
            self.cart[variant_id]['quantity'] += quantity
            
        # Ограничиваем количество остатком на складе
        if self.cart[variant_id]['quantity'] > product_variant.stock:
            self.cart[variant_id]['quantity'] = product_variant.stock
            
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product_variant):
        """Удаление товара из корзины."""
        variant_id = str(product_variant.id)
        if variant_id in self.cart:
            del self.cart[variant_id]
            self.save()

    def __iter__(self):
        """Перебор элементов в корзине и получение продуктов из базы данных."""
        variant_ids = self.cart.keys()
        variants = ProductColor.objects.filter(id__in=variant_ids).select_related('product', 'color')
        cart = deepcopy(self.cart)
        
        found_variant_ids = []
        for variant in variants:
            cart[str(variant.id)]['variant'] = variant
            found_variant_ids.append(str(variant.id))

        # Очищаем корзину от товаров, которые могли быть удалены из БД
        for variant_id in list(self.cart.keys()):
            if variant_id not in found_variant_ids:
                del self.cart[variant_id]
                self.save()
                if variant_id in cart:
                    del cart[variant_id]

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """Подсчет всех товаров в корзине."""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """Подсчет стоимости всех товаров в корзине."""
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """Удаление корзины из сессии."""
        del self.session[settings.CART_SESSION_ID]
        self.save()
