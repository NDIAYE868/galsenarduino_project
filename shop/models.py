from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ["name"]

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    short_description = models.CharField(max_length=255, blank=True)
    description = RichTextUploadingField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_new = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)
    specs = models.TextField(blank=True, help_text="Spécifications techniques (tension, portée, datasheet, etc.)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En traitement'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Paiement à la livraison'),
        ('wave', 'Wave'),
        ('om', 'Orange Money'),
    ]

    DELIVERY_METHOD_CHOICES = [
        ('dakar', 'Dakar (livraison rapide)'),
        ('regions', 'Autres régions'),
    ]

    reference = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    whatsapp_number = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100, blank=True)
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_METHOD_CHOICES)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='cod')

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Commande {self.reference}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_line_total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
