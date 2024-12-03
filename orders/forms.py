from django import forms
from orders.models import Order, Client, Material, OrderMaterial, OrderUser, User
from django.core.exceptions import ValidationError
from datetime import date
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth import get_user_model

class CreateOrderForm(forms.ModelForm):
    """Formulario para crear órdenes."""
    material = forms.ModelChoiceField(
        queryset=Material.objects.all(),
        widget=forms.Select,
        required=False,
        label="Material"
    )
    material_quantity = forms.IntegerField(
        required=False,
        label="Cantidad de material"
    )
    operator = forms.ModelChoiceField(
        queryset=User.objects.filter(role=2),  # Filtra usuarios operadores
        widget=forms.Select,
        required=False,
        label="Operador"
    )
    class Meta:
        model = Order
        fields = ['client', 'description', 'quantity', 'start_date', 'delivery_date', 'status', 'observations']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'delivery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select', 'data-bs-toggle': 'search'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        """Validaciones personalizadas."""
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        start_date = cleaned_data.get('start_date')
        delivery_date = cleaned_data.get('delivery_date')

        if quantity is not None and quantity < 0:
            self.add_error('quantity', 'La cantidad no puede ser negativa.')

        if start_date and delivery_date and delivery_date < start_date:
            self.add_error('delivery_date', 'La fecha de entrega debe ser mayor o igual a la fecha de inicio.')

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].widget.attrs.update({'class': 'form-select'})
        self.fields['material'].queryset = Material.objects.all()
        self.fields['operator'].queryset = User.objects.filter(role=2)


class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError("Esta cuenta está inactiva.", code='inactive')

    def clean_username(self):
        email = self.cleaned_data.get('username')
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            return user.username  # Retorna el `username` correspondiente al correo
        except User.DoesNotExist:
            raise forms.ValidationError("No se encontró un usuario con este correo electrónico.")
