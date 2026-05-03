from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path("", views.home, name="home"),
    path("catalogue/", views.product_list, name="product_list"),
    path("categorie/<slug:slug>/", views.product_list, name="product_list_by_category"),
    path("produit/<slug:slug>/", views.product_detail, name="product_detail"),
    path("panier/", views.cart_detail, name="cart_detail"),
    path("panier/ajouter/<int:product_id>/", views.cart_add, name="cart_add"),
    path("panier/supprimer/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("a-propos/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("politique-livraison/", views.delivery_policy, name="delivery_policy"),
    path("politique-retour/", views.return_policy, name="return_policy"),
    path("cgu/", views.terms, name="terms"),
    path("recherche/", views.search, name="search"),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
]
