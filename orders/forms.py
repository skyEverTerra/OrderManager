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
        label="Material",
        error_messages={
            'required': 'Por favor, selecciona un material.',
        }
    )
    material_quantity = forms.IntegerField(
        required=False,
        label="Cantidad de material",
        error_messages={
            'required': 'Este campo es obligatorio.',
            'invalid': 'Introduce un número válido.',
        }
    )
    operator = forms.ModelChoiceField(
        queryset=User.objects.filter(role=2),  # Filtra usuarios operadores
        widget=forms.Select,
        required=False,
        label="Operador",
                error_messages={
            'required': 'Debes seleccionar un operador.',
        }
    )
    class Meta:
        """ Atributos """
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
        error_messages = {
            'client': {'required': 'Por favor, selecciona un cliente.'},
            'description': {'required': 'Por favor, proporciona una descripción.'},
            'quantity': {'required': 'Por favor, especifica la cantidad.'},
            'start_date': {'required': 'Por favor, selecciona una fecha de inicio.'},
            'delivery_date': {'required': 'Por favor, selecciona una fecha de entrega.'},
            'status': {'required': 'Por favor, selecciona un estado.'},
        }

    def clean(self):
        """Validaciones personalizadas."""
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        start_date = cleaned_data.get('start_date')
        delivery_date = cleaned_data.get('delivery_date')
        material = cleaned_data.get('material')
        material_quantity = cleaned_data.get('material_quantity')

        required_fields = ['material_quantity', 'material', 'operator']
        for field in required_fields:
            if not cleaned_data.get(field):  # Si el campo está vacío
                self.add_error(field, 'Por favor, rellena este campo.')

        if quantity is not None and quantity < 0:
            self.add_error('quantity', 'La cantidad no puede ser negativa.')

        if start_date and delivery_date and delivery_date < start_date:
            self.add_error(
                'delivery_date', 
                'La fecha de entrega debe ser mayor o igual a la fecha de inicio.'
            )

        if material and material_quantity:
            if material_quantity > material.stock:
                self.add_error(
                    'material_quantity',
                    f"La cantidad solicitada ({material_quantity}) excede el stock disponible ({material.stock})."
                )

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].widget.attrs.update({'class': 'form-select'})
        self.fields['material'].queryset = Material.objects.all()
        self.fields['operator'].queryset = User.objects.filter(role=2)
        instance = kwargs.get('instance')  # La orden que se está editando
        
        # Establecer valores iniciales para campos personalizados
        if instance:
            # Material y cantidad
            order_material = instance.order_materials.first()
            if order_material:
                self.fields['material'].initial = order_material.material
                self.fields['material_quantity'].initial = order_material.material_quantity

            # Operador
            order_operator = instance.order_users.first()
            if order_operator:
                self.fields['operator'].initial = order_operator.user


class CustomAuthenticationForm(AuthenticationForm):
    """ Permite autenticar con correo """
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
