from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product, Category

class ProductSitemap(Sitemap):
    changefreq = "weekly"  # Fréquence de changement
    priority = 0.8         # Importance (0.0 à 1.0)

    def items(self):
        # Retourne tous les produits actifs
        return Product.objects.all()

    def lastmod(self, obj):
        # Date de dernière modification
        return obj.updated_at

    def location(self, obj):
        # URL de la page produit
        return reverse('shop:product_detail', kwargs={'slug': obj.slug})

class CategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        # Retourne toutes les catégories
        return Category.objects.all()

    def location(self, obj):
        # URL de la page catégorie
        return reverse('shop:product_list_by_category', kwargs={'slug': obj.slug})

# Sitemap pour les pages statiques
class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return [
            'shop:home',
            'shop:product_list', 
            'shop:about',
            'shop:contact',
        ]

    def location(self, item):
        return reverse(item)