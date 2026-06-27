from django.contrib import admin
from django.urls import path, include, reverse
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from shop.sitemap import ProductSitemap, CategorySitemap, StaticSitemap

# Configuration des sitemaps
sitemaps = {
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'static': StaticSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),  # ⬅️ Le chatbot est dans shop/urls.py
    path("ckeditor/", include("ckeditor_uploader.urls")),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import Sitemap

class StaticViewSitemap(Sitemap):
    def items(self):
        # liste des vues que tu veux indexer
        return [
            "home",
            "about",
            "contact",
            "delivery_policy",
            "return_policy",
            "terms",
            "product_list",
            "search",
        ]

    def location(self, item):
        return reverse(item)

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    # tes autres urls...
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]
