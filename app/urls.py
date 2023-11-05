
from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_list, name='products'),
    path('products/<int:id>', views.product_detail, name='product'),
    path('category/', views.category_list, name='category'),
    path('category-products/<int:category_id>/', views.category_product_list, name='category-products'),
    
]