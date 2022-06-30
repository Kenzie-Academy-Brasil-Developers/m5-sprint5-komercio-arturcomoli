from rest_framework import serializers

from accounts.exceptions import CannotUpdateKeyError

from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "is_seller",
            "date_joined",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "date_joined": {"read_only": True},
        }

    def create(self, validated_data: dict):
        return Account.objects.create_user(**validated_data)


class ShowSellerOnProductCreation(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_seller",
            "date_joined",
        ]


class UpdateAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_seller",
            "date_joined",
            "is_active",
            "password",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "password": {"write_only": True},
        }

    def update(self, instance: Account, validated_data: dict):
        forbidden_keys = ["is_active"]

        for key, value in validated_data.items():
            if key in forbidden_keys:
                raise CannotUpdateKeyError("is_active can't be updated!")
            setattr(instance, key, value)

        if validated_data["password"]:
            instance.set_password(validated_data["password"])

        instance.save()

        return instance


class ToggleIsActive(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_seller",
            "date_joined",
            "is_active",
        ]

        read_only_fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "is_seller",
            "date_joined",
        ]

    def update(self, instance, validated_data):
        is_active = validated_data.pop("is_active", None)
        if not is_active:
            raise CannotUpdateKeyError("is_active is required.")

        instance.is_active = is_active
        instance.save()

        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
