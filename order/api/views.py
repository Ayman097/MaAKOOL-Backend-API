# views.py
from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from app.models import Product
from order.models import Order, OrderItems
from .serializers import OrderItemsSerializer, DetailedOrderSerializer, OrderSerializer
from accounts.models import User
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import stripe
import json
import logging

from rest_framework.exceptions import AuthenticationFailed


class OrderPagination(PageNumberPagination):
    page_size = 3  # Number of items to include on each page
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        return Response(
            {
                "total_pages": self.page.paginator.num_pages,
                "results": data,
            }
        )


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = DetailedOrderSerializer
    pagination_class = OrderPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["status"]

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = DetailedOrderSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update_order_status(instance, serializer.validated_data)
        return Response(serializer.data)


class OrderItemsViewSet(viewsets.ModelViewSet):
    queryset = OrderItems.objects.all()
    serializer_class = OrderItemsSerializer

    def add_to_order(self, request, *args, **kwargs):
        userId = request.data.get("userId", None)
        if userId is not None:
            user = User.objects.filter(id=userId).first()

            product_id = request.data.get("product")
            order, created = Order.objects.get_or_create(ordered=False, user=user)
            # هنا انا بسرش ع الاوردر اللي مواصفاته اللي فوق دي وخليته هو ال default

            # Add the product to the order (assuming product exists)
            product = Product.objects.get(id=product_id)
            order_item, created = OrderItems.objects.get_or_create(
                order=order, product=product, defaults={"quantity": 1}
            )

            if not created:
                # If the order item already exists, update the quantity
                order_item.quantity += 1
                order_item.save()
                order.total_price += product.price
                order.save()
            else:
                order_item.save()
                order.total_price += product.price
                order.save()
            return Response(
                {"message": "Item added to the order successfully"},
                status=status.HTTP_201_CREATED,
            )

        else:
            raise AuthenticationFailed("User not found.")

    # Create a custom action for removing an item from the order
    def remove_from_order(self, request, *args, **kwargs):
        userId = request.data.get("userId", None)
        if userId is not None:
            user = User.objects.filter(id=userId).first()

            product_id = request.data.get("product")
            # order_id = request.data.get("order")
            # السطر دا هيستبدل باليوزر الحالي عشان اجيب الاوردر
            product = Product.objects.get(id=product_id)

            order = Order.objects.filter(ordered=False, user=user).first()  # دا مؤقت

            try:
                order_item = OrderItems.objects.get(order=order, product=product_id)
                order.total_price -= product.price * order_item.quantity
                if order.total_price >= 0:
                    order.save()
                order_item.delete()
                return Response(
                    {"message": "Item removed from the order"},
                    status=status.HTTP_204_NO_CONTENT,
                )
            except OrderItems.DoesNotExist:
                return Response(
                    {"message": "Item not found in the order"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            raise AuthenticationFailed("User not found.")

    # Create a custom action for updating the quantity of an item in the order
    def decrease_from_order(self, request, *args, **kwargs):
        userId = request.data.get("userId", None)
        if userId is not None:
            user = User.objects.filter(id=userId).first()

            product_id = request.data.get("product")
            # order_id = request.data.get("order")
            # السطر دا هيستبدل باليوزر الحالي عشان اجيب الاوردر
            product = Product.objects.get(id=product_id)

            order = Order.objects.filter(ordered=False, user=user).first()  # دا مؤقت

            try:
                order_item = OrderItems.objects.get(order=order, product=product)
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                    order.total_price -= product.price
                    order.save()
                    return Response(
                        {"message": "Item quantity has been decreased"},
                        status=status.HTTP_200_OK,
                    )
                return Response(
                    {"message": "Item quantity cannot be less than 1"},
                    status=status.HTTP_200_OK,
                )
            except OrderItems.DoesNotExist:
                return Response(
                    {"message": "Item not found in the order"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        raise AuthenticationFailed("User not found.")


@api_view(["POST"])
def submit_order(request):
    userId = request.data.get("userId", None)
    if userId is not None:
        user = User.objects.filter(id=userId).first()

        order = Order.objects.filter(ordered=False, user=user).first()
        if order:
            order.ordered = True
            order.status = "Pending"  # Set the status to 'Pending'
            order.creating_date = timezone.now()
            order.save()
            return Response(
                {"message": "Successfully submitted order"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "No order found to submit"},
                status=status.HTTP_404_NOT_FOUND,
            )
    raise AuthenticationFailed("User not found.")


from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = "page_size"
    max_page_size = 1000


@api_view()
def userOrders(request, id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    order_direction = request.query_params.get("order", "asc")
    ordering = "creating_date" if order_direction == "asc" else "-creating_date"

    userOrders = (
        Order.objects.filter(user=user, ordered=True).order_by(ordering).distinct()
    )

    paginator = CustomPageNumberPagination()
    result_page = paginator.paginate_queryset(userOrders, request)

    if userOrders.exists():
        userOrderSerializer = DetailedOrderSerializer(result_page, many=True)
        return Response(
            {
                "userOrders": userOrderSerializer.data,
                "total_pages": paginator.page.paginator.num_pages,
            },
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {"message": "No ordered items found for this user"},
            status=status.HTTP_204_NO_CONTENT,
        )


stripe.api_key = "sk_test_51OCud2FDejSiAyCJUmWs68SyHkOowWlNeEsLalIe68YyofMjj0ZGVus9fp6W70f714Cme4ccTZODayIKKjuUTAm3004u6PetAI"

# Set up logging
logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def create_checkout_session(request):
    try:
        data = json.loads(request.body.decode("utf-8"))

        custom_amount = float(data.get("amount"))

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "EGP",
                        "product_data": {
                            "name": "Total",
                            "images": [
                                "https://assets.theedgemarkets.com/digital-trade-ent-tem1305_20200212155358_theedgemarkets.jpg?null"
                            ],
                        },
                        "unit_amount": int(custom_amount * 100),
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="http://localhost:5173/cart/success",
            cancel_url="http://localhost:5173/cart/fail",
        )

        session_id = session.id
        return JsonResponse(
            {"client_secret": session.client_secret, "sessionId": session_id}
        )

    except Exception as e:
        # Log the error for debugging purposes
        logger.exception("Error creating Checkout Session:")
        return JsonResponse({"error": str(e)}, status=500)
