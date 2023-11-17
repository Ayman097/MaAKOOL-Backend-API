
from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_list, name='products'),
    path('products/<int:id>', views.product_detail, name='product'),
    path('category/', views.category_list, name='category'),
    path('category-products/<int:category_id>/', views.category_product_list, name='category-products'),

    # Admin or Staff only
    path('products/new',  views.new_product, name='new_product'),
    path('products/edit/<int:id>',  views.edit_product, name='edit_product'),
    path('products/delete/<int:id>',  views.delete_product, name='delete_product'),

    path('category/new',  views.new_category, name='new_category'),
    path('category/edit/<int:id>',  views.update_category, name='update_category'),
    path('category/delete/<int:id>',  views.delete_category, name='delete_category'),

    path('offer/',  views.get_offers, name='offer'),
    path('offer/add',  views.add_offers, name='add-offer'),
    path('offer/update/<int:id>',  views.update_offers, name='update-offer'),
    path('offer/delete/<int:id>',  views.delete_offers, name='delete-offer'),
]