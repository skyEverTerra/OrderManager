from django.shortcuts import render
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from orders.models import Order, Client, OrderUser, User, OrderStatus
from orders.forms import *
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.forms import modelformset_factory
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string

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
    paginate_by = 5

    def get_queryset(self):
        # Prefetch operadores y materiales relacionados
        order_by = self.request.GET.get('order_by', 'delivery_date')
        select_by = self.request.GET.get('select_by', None)
        valid_order_fields = ['id', 'delivery_date', 'start_date']

        if order_by not in valid_order_fields:
            order_by = 'delivery_date'

        queryset = (
            Order.objects.select_related("client", "status", "created_by")
            .prefetch_related("order_users__user")
        )

        if select_by:
            queryset = queryset.filter(status__status=select_by)
            return queryset.order_by(order_by)
        
        excluded_statuses = ['archivado', 'cancelado']
        queryset = queryset.exclude(status__status__in=excluded_statuses)

        return queryset.order_by(order_by)

    def get(self, request, *args, **kwargs):
        # Si es una solicitud AJAX, retornar los datos en JSON
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            rendered_orders = render_to_string('orders/partials/order_list.html', {'orders': context['orders']})
            return JsonResponse({'orders': rendered_orders}, status=200)
        return super().get(request, *args, **kwargs)


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
        context = super().get_context_data(**kwargs)
        order_operator = self.object.order_users.first()

        if order_operator:
            context['operator_selected'] = order_operator.user

        return context

    def form_valid(self, form):
        """Actualizar la orden junto con material y operador seleccionados."""
        form.instance.created_by = self.request.user
        response = super().form_valid(form)

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
