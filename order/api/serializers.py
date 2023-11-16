from rest_framework import serializers
from ..models import Order, OrderItems
from app.models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "user",
            "total_price",
            "creating_date",
            "status",
            "ordered",
            "orderItems",
        ]


class OrderItemsSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItems
        fields = ["product", "quantity"]


class DetailedOrderSerializer(serializers.ModelSerializer):
    orderItems = OrderItemsSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "user",
            "total_price",
            "creating_date",
            "status",
            "ordered",
            "orderItems",
        ]
