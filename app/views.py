from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from .models import Product, Category, Offer
from .serializers import ProductSerializer, CategorySerializer, OfferSerializer
from decimal import Decimal
from .filters import ProductFilter


# Create your views here.
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


# For Admin Dashboard
# Create Product
@api_view(["POST"])
# @permission_classes([IsAuthenticated])
def new_product(request):
    data = request.data
    category_name = data.get("category", [])[0:]

    print(f"Attempting to find category with name: '{category_name}'")

    try:
        category = Category.objects.get(name__iexact=category_name)
    except Category.DoesNotExist:
        return Response({"error": f'Category "{category_name}" does not exist'})

    # Assign the Category instance to the data dictionary
    data["category"] = category.id
    serializer = ProductSerializer(data=data)

    print("Data Serializers: ", serializer)
    print("serializer.is_valid() STATUS: ", serializer.is_valid())
    print(serializer.errors)
    if serializer.is_valid():
        # product = Product.objects.create(**data) # , user=request.user
        # res = ProductSerializer(product)
        product = serializer.save()
        res = ProductSerializer(product)
        return Response({"product": res.data}, status=status.HTTP_201_CREATED)

    return Response({"error": "invalid data"})


# Admin Edit Product
@api_view(["PUT"])
# @permission_classes([IsAuthenticated])
def edit_product(request, id):
    product = get_object_or_404(Product, pk=id)

    # if product.user != request.user:
    #     return Response({'Error': "You can't Update  this product"}, status=status.HTTP_401_UNAUTHORIZED)

    product.name = request.data["name"]
    product.description = request.data["description"]
    product.price = Decimal(request.data["price"])
    product.image = request.data["image"]

    category = Category.objects.get(name=request.data["category"])
    product.category = category

    product.save()

    serializer = ProductSerializer(product)

    return Response({"product": serializer.data})


# Delete Product
@api_view(["DELETE"])
# @permission_classes([IsAuthenticated])
def delete_product(request, id):
    product = get_object_or_404(Product, pk=id)

    # if product.user != request.user:
    #     return Response({'Error': "You can't Update  this product"}, status=status.HTTP_401_UNAUTHORIZED)

    product.delete()

    return Response({"product": "Deleted Successfully"})


# Create Category
@api_view(["POST"])
def new_category(request):
    data = request.data

    category = Category.objects.create(name=data["name"])

    serializer = CategorySerializer(category)
    return Response(serializer.data)


# Update Category
@api_view(["PUT"])
def update_category(request, id):
    category = get_object_or_404(Category, pk=id)

    category.name = request.data["name"]
    category.save()

    serializer = CategorySerializer(category)
    return Response(serializer.data)


# Delete Category
@api_view(["DELETE"])
def delete_category(request, id):
    category = get_object_or_404(Category, pk=id)
    category.delete()

    return Response({"category": "Deleted Successfully"})


# Offers Handling


@api_view()
def get_offers(request):
    offers = Offer.objects.all()
    serializer = OfferSerializer(offers, many=True)
    return Response(serializer.data)


# Add Offer
@api_view(["POST"])
def add_offers(request):
    data = request.data
    offer = Offer.objects.create(image=data["image"])
    offer.save()
    serializer = OfferSerializer(offer)
    return Response({"offer": serializer.data}, status=status.HTTP_201_CREATED)


# Update Offer
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
