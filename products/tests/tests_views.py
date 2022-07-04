import ipdb
from accounts.models import Account
from products.models import Product
from products.serializers import (
    ProductCreationSerializer,
    ProductListSerializer,
)
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework.views import status


class TestProductsViews(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user_admin = {
            "email": "admin@admin.com",
            "password": "1234",
            "first_name": "Admin",
            "last_name": "User",
        }

        cls.user_seller = {
            "email": "john@doe.com",
            "password": "abcd",
            "first_name": "John",
            "last_name": "Doe",
            "is_seller": True,
        }

        cls.user_seller_2 = {
            "email": "john2@doe.com",
            "password": "abcd",
            "first_name": "John",
            "last_name": "Doe",
            "is_seller": True,
        }

        cls.user_not_seller = {
            "email": "jane@doe.com",
            "password": "abcd",
            "first_name": "Jane",
            "last_name": "Doe",
            "is_seller": False,
        }

        cls.product = {
            "description": "test description",
            "price": 10.50,
            "quantity": 50,
        }

        cls.admin = Account.objects.create_superuser(**cls.user_admin)
        cls.seller = Account.objects.create_user(**cls.user_seller)
        cls.seller_2 = Account.objects.create_user(**cls.user_seller_2)
        cls.user = Account.objects.create_user(**cls.user_not_seller)

        cls.products = [
            Product.objects.create(
                description=f"description {product_id}",
                price=10.99,
                quantity=50,
                seller=cls.seller,
            )
            for product_id in range(1, 50)
        ]

        cls.token_admin = Token.objects.create(user=cls.admin)
        cls.token_seller = Token.objects.create(user=cls.seller)
        cls.token_seller2 = Token.objects.create(user=cls.seller_2)
        cls.token_user = Token.objects.create(user=cls.user)

    def test_product_creation_no_token(self):
        response = self.client.post("/api/products/", data=self.product)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_product_creation_common_user(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.token_user.key
        )

        response = self.client.post("/api/products/", data=self.product)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_creation_admin_user(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.token_admin.key
        )

        response = self.client.post("/api/products/", data=self.product)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_product_creation_success(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.token_seller.key
        )

        response = self.client.post("/api/products/", data=self.product)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("description", response.data)
        self.assertIn("price", response.data)
        self.assertIn("quantity", response.data)
        self.assertIn("seller", response.data)
        self.assertIn("is_active", response.data)
        self.assertEqual(response.data["seller"]["id"], self.seller.id)
        self.assertEqual(response.data["seller"]["email"], self.seller.email)
        self.assertEqual(
            response.data["seller"]["first_name"], self.seller.first_name
        )
        self.assertEqual(
            response.data["seller"]["last_name"], self.seller.last_name
        )
        self.assertEqual(
            response.data["seller"]["is_seller"], self.seller.is_seller
        )

    def test_product_creation_negative_quantity(self):
        product_data = {
            "description": "test description",
            "price": 10.50,
            "quantity": -50,
        }

        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.token_seller.key
        )

        response = self.client.post("/api/products/", data=product_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("quantity", response.data)
        self.assertIn(
            "Ensure this value is an integer bigger than 0",
            response.data["quantity"],
        )

    def test_product_creation_wrong_keys(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.token_seller.key
        )

        response = self.client.post("/api/products/", data={})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)
        self.assertIn("price", response.data)
        self.assertIn("quantity", response.data)

    def test_product_list_all(self):

        response = self.client.get("/api/products/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.products), len(response.data))

        for product in self.products:
            self.assertIn(
                ProductListSerializer(instance=product).data, response.data
            )

    def test_product_filter(self):
        response = self.client.get("/api/products/4/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            ProductListSerializer(instance=self.products[3]).data,
        )

    def test_trying_to_patch_product_failure(self):
        product = Product.objects.create(seller=self.seller, **self.product)

        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.token_seller2.key
        )

        response = self.client.patch(
            f"/api/products/{product.id}/", data={"description": "Teste patch"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn(
            "You do not have permission to perform this action.",
            response.data["detail"],
        )

    def test_product_patch_success(self):
        product = Product.objects.create(seller=self.seller, **self.product)

        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.token_seller.key
        )

        response = self.client.patch(
            f"/api/products/{product.id}/", data={"description": "Teste patch"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("id", response.data)
        self.assertIn("seller", response.data)
        self.assertIn("description", response.data)
        self.assertIn("price", response.data)
        self.assertIn("quantity", response.data)
        self.assertIn("is_active", response.data)
        self.assertEqual(response.data["description"], "Teste patch")
