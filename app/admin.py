from django.contrib import admin
from . import models
from django.utils.html import format_html
# Register your models here.


# @admin.register(models.Customer)
# class CustomerAdmin(admin.ModelAdmin):
#     list_display = ['first_name', 'last_name', 'membership']
#     list_editable = ['membership']
#     list_per_page = 10
#     search_fields = ['first_name']


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    list_editable = ['price']



@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

# admin.site.register(Product)