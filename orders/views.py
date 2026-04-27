from django.shortcuts import render, redirect
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from urllib.parse import quote

def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('cart:cart_detail')
        
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.total_cost = cart.get_total_price()
            order.save()
            
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product_variant=item['variant'],
                    product_name=f"{item['variant'].product.name} ({item['variant'].color.name})",
                    price=item['price'],
                    quantity=item['quantity']
                )
                
            # Очищаем корзину
            cart.clear()
            
            # Формируем сообщение для Telegram
            telegram_username = "aminaaamiiir" # ЗАМЕНИТЕ НА ВАШ ЮЗЕРНЕЙМ В ТЕЛЕГРАМЕ
            
            text = f"📦 Новый заказ №{order.id}\n\n"
            text += f"👤 Имя: {order.name}\n"
            text += f"📞 Телефон: {order.phone}\n\n"
            text += "🛍 Товары:\n"
            
            for item in order.items.all():
                text += f"• {item.product_name} — {item.quantity} шт. ({item.get_cost()} сум)\n"
                
            text += f"\n💰 Итого к оплате: {order.total_cost} сум"
            
            encoded_text = quote(text)
            telegram_url = f"https://t.me/{telegram_username}?text={encoded_text}"
            
            # Редирект в телеграм
            return redirect(telegram_url)
    else:
        form = OrderCreateForm()
        
    return render(request, 'orders/checkout.html', {'cart': cart, 'form': form})
