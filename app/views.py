from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from accounts.models import Rating, User

from .models import Product, Category, Offer
from .serializers import ProductSerializer, CategorySerializer, OfferSerializer
from decimal import Decimal
from rest_framework.views import APIView

from .filters import ProductFilter


@api_view()
def product_list(request):
    products = Product.objects.all()
    filterset = ProductFilter(request.GET, queryset=products)

    pageNum = 12
    paginator = PageNumberPagination()
    paginator.page_size = pageNum

    queryset = paginator.paginate_queryset(filterset.qs, request)
    serializer = ProductSerializer(queryset, many=True)

    return paginator.get_paginated_response(serializer.data)


@api_view()
def product_detail(request, id):
    product = get_object_or_404(Product, pk=id)
    print(product, product.price, product.description)
    serializer = ProductSerializer(product)
    return Response(serializer.data)


@api_view()
def category_list(request):
    category = Category.objects.all()

    serializer = CategorySerializer(category, many=True)
    return Response(serializer.data)


@api_view()
def category_product_list(request, category_id):
    try:
        queryset = Product.objects.filter(category=category_id)
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def new_product(request):
    data = request.data
    category_name = data.get("category", None)

    if category_name is None:
        return Response({"error": "Category field is required"})

    category_name = category_name.strip('"')

    try:
        category = Category.objects.get(name__iexact=category_name)
    except Category.DoesNotExist:
        return Response({"error": f'Category "{category_name}" does not exist'})

    data["category"] = category.id

    is_deleted = data.get("is_deleted")
    if is_deleted is not None:
        data["is_deleted"] = is_deleted.strip('"').lower() == "true"

    serializer = ProductSerializer(data=data)

    if serializer.is_valid():
        product = serializer.save()
        res = ProductSerializer(product)
        return Response({"product": res.data}, status=status.HTTP_201_CREATED)

    return Response({"error": serializer.errors})


@api_view(["PUT"])
def edit_product(request, id):
    product = get_object_or_404(Product, pk=id)

    product.name = request.data["name"]
    product.description = request.data["description"]
    product.price = Decimal(request.data["price"])
    product.image = request.data["image"]

    category = Category.objects.get(name=request.data["category"])
    product.category = category

    product.save()

    serializer = ProductSerializer(product)

    return Response({"product": serializer.data})


@api_view(["DELETE"])
def delete_product(request, id):
    product = get_object_or_404(Product, pk=id)

    product.delete()

    return Response({"product": "Deleted Successfully"})


@api_view(["POST"])
def new_category(request):
    data = request.data

    category = Category.objects.create(name=data["name"])

    serializer = CategorySerializer(category)
    return Response(serializer.data)


@api_view(["PUT"])
def update_category(request, id):
    category = get_object_or_404(Category, pk=id)

    category.name = request.data["name"]
    category.save()

    serializer = CategorySerializer(category)
    return Response(serializer.data)


@api_view(["DELETE"])
def delete_category(request, id):
    category = get_object_or_404(Category, pk=id)
    category.delete()

    return Response({"category": "Deleted Successfully"})


@api_view()
def get_offers(request):
    offers = Offer.objects.all()
    serializer = OfferSerializer(offers, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def add_offers(request):
    data = request.data
    offer = Offer.objects.create(
        image=data["image"], start_date=data["start_date"], end_date=data["end_date"]
    )
    offer.save()
    serializer = OfferSerializer(offer)
    return Response({"offer": serializer.data}, status=status.HTTP_201_CREATED)


@api_view(["PUT"])
def update_offers(request, id):
    offer = get_object_or_404(Offer, id=id)

    offer.image = request.data["image"]
    offer.save()

    serializer = OfferSerializer(offer)
    return Response(serializer.data)


@api_view(["DELETE"])
def delete_offers(request, id):
    offer = get_object_or_404(Offer, id=id)
    offer.delete()
    return Response({"Offer": "Deleted Successfully"})


class RateProductView(APIView):
    def post(self, request):
        product_id = request.data.get("product_id")
        user_id = request.data.get("user_id")
        rating_value = request.data.get("rating_value")

        if not all([product_id, user_id, rating_value]):
            return Response(
                {"error": "Incomplete data provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=user_id)
            product = Product.objects.get(id=product_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User does not exist."}, status=status.HTTP_404_NOT_FOUND
            )
        except Product.DoesNotExist:
            return Response(
                {"error": "Product does not exist."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            rating, created = Rating.objects.update_or_create(
                user=user, product=product, defaults={"rating": rating_value}
            )

            product.update_average_rating()

            updated_product_data = {
                "avg_rating": product.avg_rating,
                "total_ratings": product.total_ratings,
            }

            return Response(
                {
                    "success": True,
                    "message": "Rating updated successfully.",
                    "product_data": updated_product_data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
