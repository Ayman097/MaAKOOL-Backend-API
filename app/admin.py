from django.contrib import admin
from . import models
from django.utils.html import format_html
# Register your models here.





@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    list_editable = ['price']



@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

# admin.site.register(Product)