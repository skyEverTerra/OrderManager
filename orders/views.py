from django.shortcuts import render
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from orders.models import Order, Client, Material, OrderMaterial, OrderUser, User, OrderStatus
from orders.forms import *
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.forms import modelformset_factory
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def add_client_ajax(request):
    """Vista para agregar clientes vía AJAX."""
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            client = Client.objects.create(name=name)
            return JsonResponse({"success": True, "client_id": client.id, "client_name": client.name}, status=201)
        return JsonResponse({"success": False, "error": "Nombre del cliente es obligatorio."}, status=400)

def user_redirect(request):
    """ Redirecciona """
    privileges = request.user.role - 1
    to_url = (
        'order_list', # Si es administrador
    )
    return redirect(to_url[privileges])

# Create your views here.
# class ManagementView(TemplateView, LoginRequiredMixin):
#     """ Order management view """
#     template_name = "orders/management.html"

class ManagementView(ListView):
    """Vista de administración para listar órdenes."""
    model = Order
    template_name = "orders/management.html"
    context_object_name = "orders"
    paginate_by = 10

    def get_queryset(self):
        # Prefetch operadores y materiales relacionados
        return (
            Order.objects.select_related("client", "status", "created_by")
            .prefetch_related("order_users__user", "order_materials__material")
            .order_by("-start_date")
        )


class CreateOrderView(LoginRequiredMixin, CreateView):
    """Vista para crear órdenes."""
    model = Order
    form_class = CreateOrderForm
    template_name = "orders/create.html"
    success_url = reverse_lazy("order_list")

    def form_valid(self, form):
        """Asignar el usuario autenticado como creador."""
        form.instance.created_by = self.request.user
        return super().form_valid(form)
