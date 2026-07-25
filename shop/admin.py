from django.contrib import admin
from .models import Category, Product, ProductImage, Order, OrderItem, ContactMessage

# ============================
#  CATEGORY ADMIN
# ============================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


# ============================
#  PRODUCT IMAGES INLINE
# ============================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3   # nombre de champs images affichés par défaut
    readonly_fields = []
    fields = ("image",)


# ============================
#  PRODUCT ADMIN
# ============================
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "is_active", "is_new", "is_popular")
    list_filter = ("category", "is_active", "is_new", "is_popular")
    search_fields = ("name", "short_description", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]  # ⬅️ permet d'ajouter plusieurs images


# ============================
#  ORDER ITEM INLINE
# ============================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "unit_price")


# ============================
#  ORDER ADMIN
# ============================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("reference", "first_name", "total_amount", "status", "created_at")
    list_filter = ("status", "delivery_method", "payment_method")
    search_fields = ("reference", "first_name", "whatsapp_number")
    inlines = [OrderItemInline]
    readonly_fields = ("reference", "total_amount", "shipping_fees", "created_at")


# ============================
#  CONTACT MESSAGE ADMIN
# ============================
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "whatsapp", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "message")
    readonly_fields = ("name", "email", "whatsapp", "message", "created_at")
    actions = ["mark_as_read", "mark_as_unread"]

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, "Les messages sélectionnés ont été marqués comme lus.")
    mark_as_read.short_description = "Marquer comme lu"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, "Les messages sélectionnés ont été marqués comme non lus.")
    mark_as_unread.short_description = "Marquer comme non lu"

