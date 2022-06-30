import ipdb
from accounts.models import Account
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import Response, status
from utils.mixins import SerializerByMethodMixin

from products.permissions import (
    AuthenticatedSellerOrReadOnly,
    ProductSellerOwner,
)
from products.serializers import (
    ProductCreationSerializer,
    ProductListSerializer,
)

from .models import Product


class ProductsView(SerializerByMethodMixin, generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [AuthenticatedSellerOrReadOnly]

    queryset = Product.objects.all()
    serializer_map = {
        "GET": ProductListSerializer,
        "POST": ProductCreationSerializer,
    }

    def perform_create(self, serializer):
        seller = self.request.user

        serializer.save(seller=seller)


class ProductsDetailsView(
    SerializerByMethodMixin, generics.RetrieveUpdateAPIView
):

    authentication_classes = [TokenAuthentication]
    permission_classes = [ProductSellerOwner]

    queryset = Product.objects.all()
    serializer_map = {
        "GET": ProductListSerializer,
        "PATCH": ProductCreationSerializer,
    }
