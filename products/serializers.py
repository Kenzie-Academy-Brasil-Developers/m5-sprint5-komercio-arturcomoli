from accounts.serializers import AccountSerializer, ShowSellerOnProductCreation
from rest_framework import serializers

from .models import Product


class ProductCreationSerializer(serializers.ModelSerializer):
    seller = ShowSellerOnProductCreation(read_only=True)

    class Meta:
        model = Product
        fields = "__all__"
        # extra_kwargs = {"seller": {"read_only": True}}
        depth = 1

    def validate_quantity(self, quantity):
        if quantity <= 0:
            raise serializers.ValidationError(
                "Ensure this value is an integer bigger than 0"
            )
        return quantity


class ProductListSerializer(serializers.ModelSerializer):
    seller_id = serializers.IntegerField(read_only=True, source="seller.id")

    class Meta:
        model = Product
        fields = ["description", "price", "quantity", "is_active", "seller_id"]
