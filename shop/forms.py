from django import forms
from .models import Order, ContactMessage

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
                "placeholder": "Ex : 77 123 45 67"
            }),
            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Ex : Liberté 6, Dakar"
            }),
        }

    def clean_whatsapp_number(self):
        number = self.cleaned_data.get('whatsapp_number')
        if not number:
            return number
            
        # Nettoyage : retirer les espaces, tirets, points et parenthèses
        cleaned = number.replace(' ', '').replace('-', '').replace('.', '').replace('(', '').replace(')', '')
        
        # Retirer le préfixe pays Sénégal (+221 ou 221) si présent
        if cleaned.startswith('+221'):
            cleaned = cleaned[4:]
        elif cleaned.startswith('221'):
            cleaned = cleaned[3:]
            
        # Vérifier qu'il reste exactement 9 chiffres (format national Sénégal)
        if not cleaned.isdigit() or len(cleaned) != 9:
            raise forms.ValidationError("Veuillez saisir un numéro de téléphone sénégalais valide à 9 chiffres (ex: 77 123 45 67).")
            
        return cleaned


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "whatsapp", "message"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Votre nom complet"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Ex : exemple@gmail.com"
            }),
            "whatsapp": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Facultatif"
            }),
            "message": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Écrivez votre message ici..."
            }),
        }

    def clean_whatsapp(self):
        number = self.cleaned_data.get('whatsapp')
        if not number:
            return number
            
        # Nettoyage
        cleaned = number.replace(' ', '').replace('-', '').replace('.', '').replace('(', '').replace(')', '')
        
        # Retirer préfixe pays Sénégal
        if cleaned.startswith('+221'):
            cleaned = cleaned[4:]
        elif cleaned.startswith('221'):
            cleaned = cleaned[3:]
            
        # Validation
        if not cleaned.isdigit() or len(cleaned) != 9:
            raise forms.ValidationError("Veuillez saisir un numéro de téléphone sénégalais valide à 9 chiffres (ex: 77 123 45 67).")
            
        return cleaned

