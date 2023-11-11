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
        fields = ["total_price", "creating_date", "status", "ordered", "orderItems"]


class OrderItemsSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItems
        fields = ["product", "quantity", "order"]


class DetailedOrderSerializer(serializers.ModelSerializer):
    orderItems = OrderItemsSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["total_price", "creating_date", "status", "ordered", "orderItems"]
