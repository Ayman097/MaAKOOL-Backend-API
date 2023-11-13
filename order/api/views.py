# views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from app.models import Product
from order.models import Order, OrderItems
from .serializers import OrderSerializer, OrderItemsSerializer, DetailedOrderSerializer
from datetime import datetime
from account.models import User, Profile
import jwt


from rest_framework.exceptions import AuthenticationFailed


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = DetailedOrderSerializer


class OrderItemsViewSet(viewsets.ModelViewSet):
    queryset = OrderItems.objects.all()
    serializer_class = OrderItemsSerializer

    def add_to_order(self, request, *args, **kwargs):
        token = request.COOKIES.get("jwt")

        if not token:
            raise AuthenticationFailed("Unauthenticated.")

        try:
            payload = jwt.decode(token, "your_secret_key", algorithms=["HS256"])
            user = User.objects.filter(id=payload["id"]).first()

            if not user:
                raise AuthenticationFailed("User not found.")
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

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated.")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token.")

    # Create a custom action for removing an item from the order
    def remove_from_order(self, request, *args, **kwargs):
        token = request.COOKIES.get("jwt")

        if not token:
            raise AuthenticationFailed("Unauthenticated.")

        try:
            payload = jwt.decode(token, "your_secret_key", algorithms=["HS256"])
            user = User.objects.filter(id=payload["id"]).first()

            if not user:
                raise AuthenticationFailed("User not found.")
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
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated.")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token.")

    # Create a custom action for updating the quantity of an item in the order
    def decrease_from_order(self, request, *args, **kwargs):
        product_id = request.data.get("product")
        # order_id = request.data.get("order")
        product = Product.objects.get(id=product_id)

        order = Order.objects.filter(ordered=False).first()  # دا مؤقت

        # محتاج هنا ابقي اسرش باستخدام العميل بشششوف في جدول الأوردر لو فيه اوردر العميل بتاعه هو اللي موجود دلوقتي و الاوردر دا لسه مفتوح
        try:
            product = Product.objects.get(id=product_id)
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


from django.utils import timezone


@api_view(["POST"])
def submit_order(request):
    order = Order.objects.filter(ordered=False).first()
    # user=User.objects.filter(id=payload['id'])  # هنا هزود اني ادور باليوزر
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
            {"message": "No order found to submit"}, status=status.HTTP_404_NOT_FOUND
        )
