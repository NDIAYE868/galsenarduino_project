from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "first_name",
            "whatsapp_number",
            "address",
        ]

        labels = {
            "first_name": "Prénom",
            "whatsapp_number": "Numéro WhatsApp",
            "address": "Adresse complète",
        }

        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex : Awa"
            }),
            "whatsapp_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ex : 77 123 45 67",
                "pattern": "[0-9]{9}"
            }),
            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Ex : Liberté 6, Dakar"
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
