from django.db import models
from django.utils.html import mark_safe

# Create your models here.
from django.db import models


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def restore(self):
        self.is_deleted = False
        self.save()

    class Meta:
        abstract = True


class Category(SoftDeleteModel, models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Offer(models.Model):
    image = models.ImageField(upload_to="offers/")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def img_preview(self):
        return mark_safe(
            f'<img src = "{self.image.url}" width = "200" height = "200"/>'
        )


class Product(SoftDeleteModel, models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="products/")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def img_preview(self):
        return mark_safe(
            f'<img src = "{self.image.url}" width = "200" height = "200"/>'
        )
