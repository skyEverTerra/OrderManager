"""
URL configuration for OrderManager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView

from orders import views as order_views # Añadir url para ver

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", order_views.ManagementView.as_view(), name='order_list'),
    path("redirect/", order_views.user_redirect, name="redirect"),
    path("login/", order_views.UserLoginView.as_view(), name="login"),
    path("crear_orden/", order_views.CreateOrderView.as_view(), name='create_order'),
    path("add_client_ajax/", order_views.add_client_ajax, name="add_client_ajax"),
    path('logout/', LogoutView.as_view(), name='user_logout'),

    path('ord<int:pk>/', order_views.EditOrderView.as_view(), name='edit_order'),
]
