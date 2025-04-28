from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    role = models.CharField(max_length=50, default='manager')

class Company(models.Model):
    company_name = models.CharField(max_length=255)

    def __str__(self):
        return self.company_name

class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Cargo(models.Model):
    shipment_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    phone = models.CharField(max_length=100)
    payment = models.FloatField()
    currency = models.CharField(max_length=10, default='USD')
    truck = models.CharField(max_length=100, default='Тент/фура')
    payment_method = models.CharField(max_length=100, default='Наличные')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    message_id = models.BigIntegerField(null=True, blank=True)