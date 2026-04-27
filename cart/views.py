from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from main.models import ProductColor
from .cart import Cart

@require_POST
def cart_add(request, variant_id):
    cart = Cart(request)
    product_variant = get_object_or_404(ProductColor, id=variant_id)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1
        
    cart.add(product_variant=product_variant, quantity=quantity, update_quantity=False)
    
    # Если запрос от HTMX (например, с карточки товара), мы можем вернуть обновленную иконку корзины
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'main/partials/cart_icon.html', {'cart': cart})
        
    return redirect('cart:cart_detail')

def cart_remove(request, variant_id):
    cart = Cart(request)
    product_variant = get_object_or_404(ProductColor, id=variant_id)
    cart.remove(product_variant)
    
    if request.headers.get('HX-Request') == 'true':
        # Вернем обновленное содержимое страницы корзины
        return render(request, 'cart/partials/cart_content.html', {'cart': cart})
        
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

@require_POST
def cart_update(request, variant_id):
    cart = Cart(request)
    product_variant = get_object_or_404(ProductColor, id=variant_id)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1
        
    if quantity > 0:
        cart.add(product_variant=product_variant, quantity=quantity, update_quantity=True)
    else:
        cart.remove(product_variant)
        
    if request.headers.get('HX-Request') == 'true':
        return render(request, 'cart/partials/cart_content.html', {'cart': cart})
        
    return redirect('cart:cart_detail')
