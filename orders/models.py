""" Orders models """

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """ User model """
    ROL_CHOICES = [
        (1, 'Administrador'),
        (2, 'Operador'),
    ]

    role = models.IntegerField(choices=ROL_CHOICES, default=2)
    f_lastname = models.CharField(max_length=100, blank=True, null=True)
    m_lastname = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.f_lastname or ''} ({self.username})"


class Client(models.Model):
    """ Client model """
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return f"{self.name}"


class OrderStatus(models.Model):
    """ Status model"""
    status = models.CharField(max_length=20)
    color = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.status}"


class Order(models.Model):
    """ Order model """
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="orders")
    description = models.TextField() # specification description
    quantity = models.IntegerField() # solicited cuantity
    start_date = models.DateField()
    delivery_date = models.DateField()
    status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE, related_name="orders")
    observations = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_orders")

    def __str__(self):
        return f"{self.id}"


class OrderUser(models.Model):
    """ User and Order Model """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_users")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_orders")

    def __str__(self):
        return f"{self.user.username} en {self.order.description}"

