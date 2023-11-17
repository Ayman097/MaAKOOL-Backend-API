from django.db import models
from app.models import Product
from accounts.models import User
from softdelete.models import SoftDeleteManager


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    creating_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("In Progress", "In Progress"),
            ("Out for Delivery", "Out for Delivery"),
        ],
        null=True,
        blank=True,
    )
    ordered = models.BooleanField(default=False)
    objects = SoftDeleteManager()
    deleted_at = models.DateTimeField(null=True, blank=True)


class OrderItems(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="orderItems"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(default=1)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
