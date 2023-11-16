from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken


class User(AbstractUser):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def profile(self):
        try:
            return self.profile
        except Profile.DoesNotExist:
            return None


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    address = models.CharField(max_length=1000)
    phone = models.CharField(null=True, max_length=11)


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
