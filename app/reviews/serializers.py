from rest_framework import serializers

from products.serializers import ProductInfoSerializer

from .models import ProductReview


class ProductReviewListSerializer(serializers.ModelSerializer):  # type: ignore
    product_info = ProductInfoSerializer(source="product", read_only=True)

    class Meta:
        model = ProductReview
        fields = "__all__"


class ProductReviewDetailSerializer(serializers.ModelSerializer):  # type: ignore
    class Meta:
        model = ProductReview
        fields = "__all__"
        read_only_fields = ["status", "created_at", "updated_at"]
