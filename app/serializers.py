from rest_framework import serializers
from .models import *
from accounts.serializers import ReviewsSerializers

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    reviews = serializers.SerializerMethodField(method_name='get_reviews', read_only=True)
    class Meta:
        model = Product
        fields = "__all__"

        def get_reviews(self, obj):
            reviews = obj.reviews.all()
            serializer = ReviewsSerializers(reviews, many=True)
            return serializer.data


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = "__all__"
