from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from app.models import Product, SoftDeleteModel
from django.core.validators import MaxValueValidator, MinValueValidator


class User(AbstractUser, SoftDeleteModel):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def profile(self):
        try:
            return self.profile
        except Profile.DoesNotExist:
            return None

    def __str__(self):
        return f"{self.username} (Staff: {self.is_staff})"

    def get_queryset(self, request):
        return self.model.all_objects.get_queryset()


class Profile(SoftDeleteModel, models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    address = models.CharField(max_length=1000)
    phone = models.CharField(null=True, max_length=11)
    image = models.ImageField(null=True, blank=True, upload_to="user_image/")

    def get_queryset(self, request):
        return self.model.all_objects.get_queryset()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, "profile"):
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        pass


class RevokedToken(models.Model):
    token = models.CharField(max_length=255, unique=True)

    @classmethod
    def add(cls, token):
        cls.objects.create(token=token)

    @classmethod
    def is_blacklisted(cls, token):
        return cls.objects.filter(token=token).exists()


class ContactUsModel(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=11)
    text = models.TextField(max_length=300)

    def __str__(self):
        return f"{self.name}"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MaxValueValidator(5), MinValueValidator(1)]
    )

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}"

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.product.update_average_rating()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.update_average_rating()
