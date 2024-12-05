""" Model administrator """

from django.contrib import admin
from .models import User, Client, OrderStatus, Order, OrderUser




@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'f_lastname', 'm_lastname', 'role', 'email', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'first_name', 'f_lastname', 'email')
    ordering = ('username',)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('status',)
    search_fields = ('status',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'description', 'quantity', 'start_date', 'delivery_date', 'status', 'created_by')
    list_filter = ('status', 'start_date', 'delivery_date')
    search_fields = ('client__name', 'description')
    ordering = ('-start_date',)
    autocomplete_fields = ('client', 'status', 'created_by')

@admin.register(OrderUser)
class OrderUserAdmin(admin.ModelAdmin):
    list_display = ('order', 'user')
    list_filter = ('order', 'user')
    search_fields = ('order__id', 'user__username')
    autocomplete_fields = ('order', 'user')
