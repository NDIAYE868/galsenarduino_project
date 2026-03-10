from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "first_name",
            "last_name",
            "whatsapp_number",
            "address",
            "city",
            "region",
            "delivery_method",
            "payment_method",
        ]

        labels = {
            "first_name": "Prénom",
            "last_name": "Nom",
            "whatsapp_number": "Numéro WhatsApp",
            "address": "Adresse complète",
            "city": "Ville",
            "region": "Région",
            "delivery_method": "Mode de livraison",
            "payment_method": "Mode de paiement",
        }

        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex : Awa"
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex : Diop"
            }),
            "whatsapp_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex : 77 100 00 00"
            }),

            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Ex : Liberté 6, Dakar"
            }),

            "city": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex : Dakar"
            }),
            "region": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex : Région de Dakar"
            }),

            "delivery_method": forms.Select(attrs={
                "class": "form-select"
            }),
            "payment_method": forms.Select(attrs={
                "class": "form-select"
            }),
        }


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=150,
        label="Nom complet",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Votre nom complet"
        }),
    )

    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Ex : exemple@gmail.com"
        }),
    )

    whatsapp = forms.CharField(
        max_length=20,
        label="Numéro WhatsApp",
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Facultatif"
        }),
    )

    message = forms.CharField(
        label="Votre message",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 4,
            "placeholder": "Écrivez votre message ici..."
        }),
    )
