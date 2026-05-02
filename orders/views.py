from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from urllib.parse import quote
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='10/m', method='POST', block=True)
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        if request.headers.get('HX-Request'):
            response = HttpResponse()
            response['HX-Redirect'] = '/cart/'
            return response
        return redirect('cart:cart_detail')
        
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            platform = request.POST.get('platform', 'telegram')
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
                
            cart.clear()
            
            telegram_username = "aminaaamiiir"
            
            text = f"📦 Новый заказ №{order.id}\n\n"
            text += f"👤 Имя: {order.name}\n"
            text += f"📞 Телефон: {order.phone}\n\n"
            text += "🛍 Товары:\n"
            
            for item in order.items.all():
                text += f"• {item.product_name} — {item.quantity} шт. ({item.get_cost()} сум)\n"
                
            text += f"\n💰 Итого к оплате: {order.total_cost} сум"
            
            encoded_text = quote(text)
            
            if request.headers.get('HX-Request'):
                if platform == 'instagram':
                    instagram_username = "amico.uz"
                    return render(request, 'orders/partials/instagram_modal.html', {
                        'order': order,
                        'text': text,
                        'redirect_url': f"https://ig.me/m/{instagram_username}"
                    })
                else:
                    telegram_url = f"https://t.me/{telegram_username}?text={encoded_text}"
                    response = HttpResponse()
                    response['HX-Redirect'] = telegram_url
                    return response

            telegram_url = f"https://t.me/{telegram_username}?text={encoded_text}"
            return redirect(telegram_url)
        else:
            # Форма невалидна
            if request.headers.get('HX-Request'):
                return render(request, 'orders/partials/checkout_form.html', {
                    'form': form,
                    'cart': cart
                })
    else:
        form = OrderCreateForm()
        
    return render(request, 'orders/checkout.html', {'cart': cart, 'form': form})
