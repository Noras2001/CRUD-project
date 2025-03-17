# shop\views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category
from .forms import ProductForm, CategoryForm
from django.db.models import Sum, Count, Avg, Min, Max

def product_list(request):
    products = Product.objects.all()

    # Фильтрация по категории
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    # Фильтрация по диапазону цен
    price_from = request.GET.get('price_from')
    price_to = request.GET.get('price_to')
    if price_from:
        products = products.filter(price__gte=price_from)
    if price_to:
        products = products.filter(price__lte=price_to)

    # Сортировка по цене или дате добавления
    sort_by = request.GET.get('sort_by')
    order = request.GET.get('order', 'asc')
    if sort_by in ['price', 'created_at']:
        if order == 'desc':
            sort_by = '-' + sort_by
        products = products.order_by(sort_by)

    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'shop/product_list.html', context)

# Creating a new product
def create_product(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('product_list')
    return render(request, 'shop/create_product.html', {'form': form})

# Reading a single product's details
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})

# Updating an existing product
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect('product_list')
    return render(request, 'shop/update_product.html', {'form': form})

# Deleting a product
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'shop/delete_product.html', {'product': product})

def analytics(request):
    # Общая статистика каталога
    overall_stats = {
        'total_value': Product.objects.aggregate(total=Sum('price'))['total'],
        'total_products': Product.objects.count(),
        'average_price': Product.objects.aggregate(avg=Avg('price'))['avg'],
        'min_price': Product.objects.aggregate(min=Min('price'))['min'],
        'max_price': Product.objects.aggregate(max=Max('price'))['max'],
    }

    # Статистика по категориям
    categories_stats = Category.objects.annotate(
        total_products=Count('products'),
        total_value=Sum('products__price'),
        avg_price=Avg('products__price'),
        min_price=Min('products__price'),
        max_price=Max('products__price'),
    )

    context = {
        'overall_stats': overall_stats,
        'categories_stats': categories_stats,
    }
    return render(request, 'shop/analytics.html', context)
