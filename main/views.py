from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, DetailView, View
from django.template.response import TemplateResponse
from django.db.models import Q, Prefetch, Min

from .models import Category, Product, Color, ProductColor, Banner


SORT_OPTIONS = [
    ('Новинки', 'newest'),
    ('Цена: по возрастанию', 'price_asc'),
    ('Цена: по убыванию', 'price_desc'),
    ('По названию А–Я', 'name_asc'),
    ('По названию Я–А', 'name_desc'),
]

SORT_MAP = {
    'newest': '-created_at',
    'price_asc': 'price',
    'price_desc': '-price',
    'name_asc': 'name',
    'name_desc': '-name',
}


# -------------------- INDEX PAGE --------------------

class IndexView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': Category.objects.all(),
            'banners': Banner.objects.filter(is_active=True).order_by('order'),
            'products': Product.objects.prefetch_related(
                'product_variants__color',
                'product_variants__images',
            ).order_by('-created_at')[:8],
        })
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'main/partials/home_content.html', context)
        return TemplateResponse(request, self.template_name, context)


# -------------------- CATALOG VIEW --------------------

class CatalogView(TemplateView):
    template_name = 'main/catalog_page.html'

    def get_products(self, **kwargs):
        sort = self.request.GET.get('sort', 'newest')
        order = SORT_MAP.get(sort, '-created_at')

        products = Product.objects.prefetch_related(
            'product_variants__color',
            'product_variants__images',
        ).order_by(order)

        category_slug = kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=category)
        else:
            categories = self.request.GET.getlist('category')
            if categories:
                products = products.filter(category__slug__in=categories)

        q = self.request.GET.get('q')
        if q:
            products = products.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            )

        color = self.request.GET.get('color')
        if color:
            products = products.filter(product_variants__color__name__iexact=color)

        min_price = self.request.GET.get('min_price')
        if min_price:
            try:
                products = products.filter(price__gte=float(min_price))
            except ValueError:
                pass

        max_price = self.request.GET.get('max_price')
        if max_price:
            try:
                products = products.filter(price__lte=float(max_price))
            except ValueError:
                pass

        return products.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category_slug = kwargs.get('category_slug')
        current_category = None
        if category_slug:
            current_category = get_object_or_404(Category, slug=category_slug)

        current_sort = self.request.GET.get('sort', '')
        current_color = self.request.GET.get('color', '')
        current_min_price = self.request.GET.get('min_price', '')
        current_max_price = self.request.GET.get('max_price', '')

        # Count active filters for badge
        active_count = sum([
            bool(current_color),
            bool(current_min_price),
            bool(current_max_price),
            bool(current_sort and current_sort != 'newest'),
        ])

        context.update({
            'categories': Category.objects.all(),
            'colors': Color.objects.all(),
            'products': self.get_products(**kwargs),
            'current_category': current_category,
            'search_query': self.request.GET.get('q', ''),
            'sort_options': SORT_OPTIONS,
            'current_sort': current_sort,
            'current_color': current_color,
            'current_min_price': current_min_price,
            'current_max_price': current_max_price,
            'active_filter_count': active_count if active_count > 0 else None,
        })
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if request.headers.get('HX-Request'):
            if request.headers.get('HX-Target') == 'catalog-grid':
                return TemplateResponse(request, 'main/partials/catalog_grid.html', context)
            return TemplateResponse(request, 'main/partials/catalog.html', context)

        return TemplateResponse(request, self.template_name, context)


# -------------------- PRODUCT DETAIL --------------------

class ProductDetailView(DetailView):
    model = Product
    template_name = 'main/product_page.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self):
        return Product.objects.prefetch_related(
            Prefetch(
                'product_variants',
                queryset=ProductColor.objects
                .select_related('color')
                .prefetch_related('images')
            )
        ).get(slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        variants = product.product_variants.all()

        selected_color = self.request.GET.get('color')
        selected_variant = (
            variants.filter(color__name__iexact=selected_color).first()
            if selected_color else variants.first()
        )

        context.update({
            'categories': Category.objects.all(),
            'variants': variants,
            'selected_variant': selected_variant,
            'product_images': selected_variant.images.all() if selected_variant else [],
            'related_products': Product.objects.prefetch_related(
                'product_variants__color',
                'product_variants__images',
            ).filter(category=product.category).exclude(id=product.id)[:4],
            'sort_options': SORT_OPTIONS,
            'current_sort': '',
        })
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)

        if request.headers.get('HX-Request'):
            if request.GET.get('color'):
                return TemplateResponse(request, 'main/partials/product_gallery.html', context)
            return TemplateResponse(request, 'main/partials/product_detail.html', context)

        return TemplateResponse(request, self.template_name, context)


# -------------------- PRODUCT CARD IMAGE --------------------

class ProductCardImageView(View):
    def get(self, request, *args, **kwargs):
        product = get_object_or_404(Product, id=request.GET.get('product_id'))
        color_name = request.GET.get('color')

        variant = product.product_variants.filter(
            color__name__iexact=color_name
        ).prefetch_related('images').first()

        image = variant.images.first() if variant and variant.images.exists() else None

        return TemplateResponse(
            request,
            'main/partials/product_card_image.html',
            {'image': image, 'product': product}
        )
