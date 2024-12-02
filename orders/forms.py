from django import forms
from orders.models import Order, Client, Material, OrderMaterial, OrderUser, User
from django.core.exceptions import ValidationError
from datetime import date

class CreateOrderForm(forms.ModelForm):
    """Formulario para crear órdenes."""
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
