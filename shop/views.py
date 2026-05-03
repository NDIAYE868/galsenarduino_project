import uuid
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from django.db import transaction

from .models import Category, Product, Order, OrderItem
from .forms import CheckoutForm, ContactForm

def _get_cart(session):
    return session.get("cart", {})

def _save_cart(session, cart):
    session["cart"] = cart
    session.modified = True

def home(request):
    categories = Category.objects.all()
    popular_products = Product.objects.filter(is_popular=True, is_active=True)[:8]
    new_products = Product.objects.filter(is_new=True, is_active=True).order_by("-created_at")[:8]
    context = {
        "categories": categories,
        "popular_products": popular_products,
        "new_products": new_products,
    }
    return render(request, "shop/home.html", context)

def product_list(request, slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True)

    if slug:
        category = get_object_or_404(Category, slug=slug)
        products = products.filter(category=category)

    # Basic filtering
    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")
    in_stock = request.GET.get("in_stock")

    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)
    if in_stock == "1":
        products = products.filter(stock__gt=0)

    context = {
        "category": category,
        "categories": categories,
        "products": products,
    }
    return render(request, "shop/product_list.html", context)
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)

    # Produits similaires : même catégorie, actifs, exclure le produit actuel
    related_products = (
        Product.objects
        .filter(category=product.category, is_active=True)
        .exclude(id=product.id)
        .order_by('-created_at')[:6]  # limiter à 6 produits
    )

    return render(request, "shop/product_detail.html", {
        "product": product,
        "related_products": related_products,
    })

def cart_detail(request):
    cart = _get_cart(request.session)
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)

    cart_items = []
    total = Decimal("0.00")

    for product in products:
        item = cart[str(product.id)]
        quantity = item["quantity"]
        price = Decimal(str(item["price"]))
        line_total = price * quantity
        total += line_total
        cart_items.append(
            {
                "product": product,
                "quantity": quantity,
                "price": price,
                "line_total": line_total,
            }
        )

    shipping_fees = Decimal("0.00")  # à adapter plus tard
    grand_total = total + shipping_fees

    context = {
        "cart_items": cart_items,
        "total": total,
        "shipping_fees": shipping_fees,
        "grand_total": grand_total,
    }
    return render(request, "shop/cart.html", context)

def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = _get_cart(request.session)
    product_key = str(product.id)

    quantity = int(request.POST.get("quantity", 1))

    if product_key not in cart:
        cart[product_key] = {"quantity": 0, "price": str(product.price)}

    cart[product_key]["quantity"] += quantity

    _save_cart(request.session, cart)
    messages.success(request, f"{product.name} ajouté au panier.")
    return redirect("shop:cart_detail")

def cart_remove(request, product_id):
    cart = _get_cart(request.session)
    product_key = str(product_id)
    if product_key in cart:
        del cart[product_key]
        _save_cart(request.session, cart)
        messages.success(request, "Produit supprimé du panier.")
    return redirect("shop:cart_detail")

def checkout(request):
    cart = _get_cart(request.session)
    if not cart:
        messages.warning(request, "Votre panier est vide.")
        return redirect("shop:product_list")

    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)

    total = Decimal("0.00")
    for product in products:
        item = cart[str(product.id)]
        total += Decimal(str(item["price"])) * item["quantity"]

    shipping_fees = Decimal("0.00")  # à adapter suivant la ville/région
    grand_total = total + shipping_fees

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # 1. Vérification stricte des stocks avec verrouillage pour éviter les conditions de concurrence (race conditions)
                    locked_products = Product.objects.select_for_update().filter(id__in=product_ids)
                    locked_products_dict = {str(p.id): p for p in locked_products}

                    for product_id_str in product_ids:
                        product = locked_products_dict.get(product_id_str)
                        if not product:
                            raise ValueError("Un produit de votre panier n'est plus disponible.")
                        
                        item = cart[product_id_str]
                        quantity = item["quantity"]
                        if product.stock < quantity:
                            raise ValueError(f"Le produit {product.name} n'est plus en stock suffisant (Stock disponible : {product.stock}).")
                    
                    # 2. Création de la commande
                    reference = uuid.uuid4().hex[:10].upper()
                    order = form.save(commit=False)
                    order.reference = reference
                    order.total_amount = grand_total
                    order.shipping_fees = shipping_fees
                    order.save()

                    # 3. Création des lignes de commande et mise à jour des stocks
                    for product_id_str in product_ids:
                        product = locked_products_dict[product_id_str]
                        item = cart[product_id_str]
                        quantity = item["quantity"]
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            unit_price=Decimal(str(item["price"])),
                        )
                        # update stock
                        product.stock -= quantity
                        product.save()

                # 4. Si tout s'est bien passé, on vide le panier
                _save_cart(request.session, {})

                messages.success(
                    request,
                    f"Votre commande a été enregistrée avec succès. Référence : {order.reference}",
                )
                return redirect("shop:home")
            except ValueError as e:
                # Si un produit n'a pas assez de stock, on annule et on notifie l'utilisateur
                messages.error(request, str(e))
                return redirect("shop:cart_detail")
    else:
        form = CheckoutForm()

    context = {
        "form": form,
        "total": total,
        "shipping_fees": shipping_fees,
        "grand_total": grand_total,
    }
    return render(request, "shop/checkout.html", context)

def about(request):
    return render(request, "shop/about.html")

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, "Votre message a été envoyé (simulation).")
            return redirect("shop:contact")
    else:
        form = ContactForm()
    return render(request, "shop/contact.html", {"form": form})

def delivery_policy(request):
    return render(request, "shop/delivery_policy.html")

def return_policy(request):
    return render(request, "shop/return_policy.html")

def terms(request):
    return render(request, "shop/terms.html")

def search(request):
    query = request.GET.get("q", "")
    products = []
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query)
            | Q(short_description__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        ).distinct()
    return render(request, "shop/search_results.html", {"query": query, "products": products})

# Dans shop/views.py

def cart_update(request, product_id):  # <-- Vérifie que le nom est EXACTEMENT celui-là
    cart = _get_cart(request.session)
    product_key = str(product_id)
    
    if request.method == "POST":
        try:
            new_quantity = int(request.POST.get("quantity", 1))
            if product_key in cart:
                if new_quantity > 0:
                    cart[product_key]["quantity"] = new_quantity
                    messages.success(request, "Quantité mise à jour.")
                else:
                    del cart[product_key]
                    messages.success(request, "Produit supprimé.")
                _save_cart(request.session, cart)
        except ValueError:
            messages.error(request, "Quantité invalide.")
            
    return redirect("shop:cart_detail")