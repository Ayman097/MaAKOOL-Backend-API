from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer

# Create your views here.
@api_view()
def product_list(request):
    products = Product.objects.all()
    #print(products)
    serializer = ProductSerializer(products, many=True)
    print(serializer.data)
    
    return Response(serializer.data)
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
    