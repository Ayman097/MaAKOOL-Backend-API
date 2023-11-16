from django.contrib import admin
from . import models
from django.utils.html import format_html
# Register your models here.



# @admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'img_preview']
    list_editable = ['price']
    readonly_fields = ['img_preview']


admin.site.register(models.Product, ProductAdmin)



@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(models.Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['img_preview']
    readonly_fields = ['img_preview']
