from django.db import models
from django.utils.html import mark_safe
from django.db.models import Avg


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


class Offer(SoftDeleteModel, models.Model):
    image = models.ImageField(upload_to="offers/")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def img_preview(self):
        return mark_safe(f'<img src="{self.image.url}" width="200" height="200"/>')


class Product(SoftDeleteModel, models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="products/")
    ratings = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    avg_rating = models.FloatField(default=1)
    total_ratings = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def img_preview(self):
        return mark_safe(f'<img src="{self.image.url}" width="200" height="200"/>')

    def update_average_rating(self):
        from accounts.models import Rating

        ratings = Rating.objects.filter(product=self)
        total_ratings = ratings.count()
        if total_ratings > 0:
            avg_rating = ratings.aggregate(Avg("rating"))["rating__avg"]
            self.avg_rating = avg_rating if avg_rating else 0
            self.total_ratings = total_ratings
            self.save()

        return self.avg_rating, self.total_ratings
