import uuid
import unicodedata
import urllib.request
import urllib.parse
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.conf import settings

from .models import Category, Product, Order, OrderItem
from .forms import CheckoutForm, ContactForm

def _get_cart(session):
    return session.get("cart", {})

def _save_cart(session, cart):
    session["cart"] = cart
    session.modified = True

def _send_order_email(order):
    subject = f"[GalsenArduino] Nouvelle Commande - Réf: {order.reference}"
    body = (
        f"Une nouvelle commande a été enregistrée avec succès.\n\n"
        f"DÉTAILS DU CLIENT :\n"
        f"-------------------\n"
        f"Référence Commande : {order.reference}\n"
        f"Client : {order.first_name} {order.last_name}\n"
        f"Numéro WhatsApp : {order.whatsapp_number}\n"
        f"Adresse de livraison : {order.address}\n"
        f"Mode de livraison : {order.get_delivery_method_display() if hasattr(order, 'get_delivery_method_display') else order.delivery_method}\n"
        f"Moyen de paiement : {order.get_payment_method_display() if hasattr(order, 'get_payment_method_display') else order.payment_method}\n\n"
        f"PRODUITS COMMANDÉS :\n"
        f"--------------------\n"
    )
    for item in order.items.all():
        body += f"- {item.product.name} x {item.quantity} ({item.unit_price} FCFA)\n"
    
    body += (
        f"\n--------------------\n"
        f"Montant Total : {order.total_amount} FCFA\n"
    )
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ORDER_NOTIFICATION_EMAIL, "Babacarmbathie856@gmail.com"],
            fail_silently=False,
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erreur envoi email commande {order.reference}: {e}")

def _send_contact_email(msg):
    subject = f"[GalsenArduino] Nouveau Message de Contact - {msg.name}"
    body = (
        f"Vous avez reçu un nouveau message de contact depuis le site GalsenArduino.\n\n"
        f"DÉTAILS DU MESSAGE :\n"
        f"--------------------\n"
        f"Nom : {msg.name}\n"
        f"Email : {msg.email}\n"
        f"WhatsApp : {msg.whatsapp}\n\n"
        f"Message :\n"
        f"{msg.message}\n"
    )
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erreur envoi email contact: {e}")

def _send_whatsapp_message(to_number, message):
    """Send an automated WhatsApp message via UltraMsg or generic HTTP API."""
    # Ensure number format is international (Sénégal: 221xxxxxxxxx)
    clean_number = "".join(c for c in to_number if c.isdigit())
    if not clean_number.startswith("221") and len(clean_number) == 9:
        clean_number = "221" + clean_number
    elif clean_number.startswith("00221"):
        clean_number = clean_number[2:]
        
    api_url = getattr(settings, "WHATSAPP_API_URL", None)
    instance_id = getattr(settings, "WHATSAPP_INSTANCE_ID", None)
    token = getattr(settings, "WHATSAPP_TOKEN", None)
    
    if not token or not instance_id:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("WhatsApp API non configurée. Message non envoyé.")
        return False
        
    if "instanceXXXXX" in api_url and instance_id:
        api_url = api_url.replace("instanceXXXXX", instance_id)
        
    payload = {
        "token": token,
        "to": f"+{clean_number}",
        "body": message
    }
    
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, method="POST")
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erreur envoi WhatsApp: {e}")
        return False

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

    # Sorting
    sort_by = request.GET.get("sort")
    if sort_by == "price_asc":
        sort_by = "price"
    elif sort_by == "price_desc":
        sort_by = "-price"
    elif sort_by == "name_asc":
        sort_by = "name"
    elif sort_by == "name_desc":
        sort_by = "-name"

    if sort_by in ["name", "-name", "price", "-price", "-created_at"]:
        products = products.order_by(sort_by)

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

    shipping_fees = Decimal("0.00")
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

    message = f"{product.name} ajouté au panier."

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "message": message,
            "cart_count": sum(item["quantity"] for item in cart.values())
        })

    messages.success(request, message)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))


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

    shipping_fees = Decimal("0.00")
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

                # 5. Envoi de l'e-mail de notification à l'administrateur
                _send_order_email(order)

                # 6. Envoi de la confirmation WhatsApp au client
                whatsapp_msg = (
                    f"Bonjour {order.first_name},\n\n"
                    f"Votre commande sur GalsenArduino a été enregistrée avec succès ! 🎉\n\n"
                    f"Référence : {order.reference}\n"
                    f"Montant : {order.total_amount} FCFA\n\n"
                    f"Nous allons la traiter le plus rapidement possible. Un conseiller vous contactera par WhatsApp pour confirmer la livraison.\n\n"
                    f"Merci pour votre confiance !"
                )
                _send_whatsapp_message(order.whatsapp_number, whatsapp_msg)

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
            contact_msg = form.save()
            _send_contact_email(contact_msg)
            messages.success(request, "Votre message a bien été envoyé !")
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

def _normalize_text(text):
    """Normalize text: convert to lowercase, strip accents, and remove trailing plurals."""
    if not text:
        return ""
    # Strip accents
    normalized = "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )
    # Lowercase & strip spaces
    normalized = normalized.lower().strip()
    return normalized

def _get_search_terms(query):
    """Split query into cleaned individual search terms, removing plural suffixes 's' and 'x' where appropriate."""
    terms = []
    for word in query.split():
        norm = _normalize_text(word)
        if len(norm) > 3:
            # Strip plural suffixes
            if norm.endswith("s"):
                norm = norm[:-1]
            elif norm.endswith("x"):
                if norm.endswith("aux") or norm.endswith("eux"):
                    norm = norm[:-1]
        if norm:
            terms.append(norm)
    return terms

def search(request):
    query = request.GET.get("q", "")
    products = []
    if query:
        terms = _get_search_terms(query)
        if terms:
            all_products = Product.objects.filter(is_active=True).select_related('category')
            matched_products = []
            for product in all_products:
                name_norm = _normalize_text(product.name)
                desc_norm = _normalize_text(product.description)
                short_norm = _normalize_text(product.short_description)
                cat_norm = _normalize_text(product.category.name if product.category else "")
                
                # Check if ALL terms match the product
                matches_all = True
                for term in terms:
                    if not (term in name_norm or term in desc_norm or term in short_norm or term in cat_norm):
                        matches_all = False
                        break
                if matches_all:
                    matched_products.append(product)
            products = matched_products
    return render(request, "shop/search_results.html", {"query": query, "products": products})

# Dans shop/views.py

def cart_update(request, product_id):
    cart = _get_cart(request.session)
    product_key = str(product_id)
    
    if request.method == "POST":
        try:
            new_quantity = int(request.POST.get("quantity", 1))
            if product_key in cart:
                if new_quantity > 0:
                    # Verification stock
                    product = get_object_or_404(Product, id=product_id, is_active=True)
                    if new_quantity > product.stock:
                        messages.error(request, f"Stock insuffisant pour {product.name}. Seulement {product.stock} unite(s) disponible(s).")
                    else:
                        cart[product_key]["quantity"] = new_quantity
                        messages.success(request, "Quantite mise a jour.")
                else:
                    del cart[product_key]
                    messages.success(request, "Produit supprime.")
                _save_cart(request.session, cart)
        except ValueError:
            messages.error(request, "Quantite invalide.")
            
    return redirect("shop:cart_detail")