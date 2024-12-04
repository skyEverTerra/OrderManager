from django.shortcuts import render
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from orders.models import Order, Client, Material, OrderMaterial, OrderUser, User, OrderStatus
from orders.forms import *
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.forms import modelformset_factory
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required

@csrf_exempt
def add_client_ajax(request):
    """Vista para agregar clientes vía AJAX."""
    if request.method == "POST":
        name = request.POST.get("name")
        if name: # agregar if name in Client.object. se encuentra...
            if Client.objects.filter(name=name).exists():
                return JsonResponse({"success": False, "error": "Ya existe un cliente con este nombre."}, status=400)
            client = Client.objects.create(name=name)
            return JsonResponse({"success": True, "client_id": client.id, "client_name": client.name}, status=201)
        return JsonResponse({"success": False, "error": "Nombre del cliente es obligatorio."}, status=400)

@login_required
def user_redirect(request):
    """ Redirecciona """
    privileges = request.user.role - 1
    to_url = (
        'order_list', # Si es administrador
    )
    return redirect(to_url[privileges])

class UserLoginView(LoginView):
    template_name = "login.html"
    form_class = CustomAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('order_list')
    
    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

# Create your views here.
# class ManagementView(TemplateView, LoginRequiredMixin):
#     """ Order management view """
#     template_name = "orders/management.html"

class ManagementView(LoginRequiredMixin,ListView):
    """Vista de administración para listar órdenes."""
    model = Order
    template_name = "orders/management.html"
    context_object_name = "orders"
    paginate_by = 3

    def get_queryset(self):
        # Prefetch operadores y materiales relacionados
        return (
            Order.objects.select_related("client", "status", "created_by")
            .prefetch_related("order_users__user", "order_materials__material")
            .order_by("-start_date")
        )

class CreateOrderView(LoginRequiredMixin, CreateView):
    """ Guardar orden """
    model = Order
    form_class = CreateOrderForm
    template_name = "orders/create.html"
    success_url = reverse_lazy("order_list")

    def form_valid(self, form):
        """Guardar la orden junto con material y operador seleccionados."""
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Manejo de material
        material = form.cleaned_data.get('material')
        material_quantity = form.cleaned_data.get('material_quantity')
        if material and material_quantity:
            OrderMaterial.objects.create(
                order=self.object,
                material=material,
                material_quantity=material_quantity
            )
            material.stock -= material_quantity
            if material.stock < 0:
                material.stock = 0  # Evitar negativos
            material.save()
        
        # Manejo de operador
        operator = form.cleaned_data.get('operator')
        if operator:
            OrderUser.objects.create(order=self.object, user=operator)

        return response


class EditOrderView(LoginRequiredMixin, UpdateView):
    """ Editar la orden """
    model = Order
    form_class = CreateOrderForm
    template_name = "orders/edit_order.html"
    success_url = reverse_lazy("order_list")

    def get_context_data(self, **kwargs):
        """Añadir datos adicionales al contexto para prellenar campos personalizados."""
        context = super().get_context_data(**kwargs)
        # Obtener material y operador existentes
        order_material = self.object.order_materials.first()
        order_operator = self.object.order_users.first()

        if order_material:
            context['material_selected'] = order_material.material
            context['material_quantity_selected'] = order_material.material_quantity
        if order_operator:
            context['operator_selected'] = order_operator.user

        return context

    def form_valid(self, form):
        """Actualizar la orden junto con material y operador seleccionados."""
        form.instance.created_by = self.request.user
        response = super().form_valid(form)

        # Manejo de material
        material = form.cleaned_data.get('material')
        material_quantity = form.cleaned_data.get('material_quantity')
        order_material = self.object.order_materials.first()

        if order_material:
            # Revertir el stock anterior
            order_material.material.stock += order_material.material_quantity
            order_material.material.save()

            if material and material_quantity:
                # Actualizar material
                order_material.material = material
                order_material.material_quantity = material_quantity
                order_material.save()

                # Reducir nuevo stock
                material.stock -= material_quantity
                if material.stock < 0:
                    material.stock = 0
                material.save()
        elif material and material_quantity:
            OrderMaterial.objects.create(
                order=self.object,
                material=material,
                material_quantity=material_quantity
            )
            material.stock -= material_quantity
            if material.stock < 0:
                material.stock = 0
            material.save()

        # Manejo de operador
        operator = form.cleaned_data.get('operator')
        order_operator = self.object.order_users.first()

        if order_operator:
            # Actualizar operador existente
            order_operator.user = operator
            order_operator.save()
        elif operator:
            OrderUser.objects.create(order=self.object, user=operator)

        return response

