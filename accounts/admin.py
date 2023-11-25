from django.contrib import admin
from accounts.models import ContactUsModel, Rating, User, Profile


class UserAdmin(admin.ModelAdmin):
    list_display = ["username", "email"]


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user"]


admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(ContactUsModel)
admin.site.register(Rating)
