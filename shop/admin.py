from django.contrib import admin
from .models import Category, Product, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "is_active", "is_new", "is_popular")
    list_filter = ("category", "is_active", "is_new", "is_popular")
    search_fields = ("name", "short_description", "description")
    prepopulated_fields = {"slug": ("name",)}

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "unit_price")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("reference", "first_name", "last_name", "total_amount", "status", "created_at")
    list_filter = ("status", "delivery_method", "payment_method")
    search_fields = ("reference", "first_name", "last_name", "whatsapp_number")
    inlines = [OrderItemInline]
    readonly_fields = ("reference", "total_amount", "shipping_fees", "created_at")
