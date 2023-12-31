from django.db import models
from app.models import Product
from accounts.models import User
from app.models import SoftDeleteModel

from accounts.models import User


class Order(SoftDeleteModel, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    creating_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("Pending", "Pending"),
            ("In Progress", "In Progress"),
            ("Out for Delivery", "Out for Delivery"),
            ("Delivered", "Delivered"),
        ],
        null=True,
        blank=True,
    )
    ordered = models.BooleanField(default=False)

    def get_queryset(self, request):
        return self.model.all_objects.get_queryset()


class OrderItems(SoftDeleteModel, models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="orderItems"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(default=1)

    def get_queryset(self, request):
        return self.model.all_objects.get_queryset()
