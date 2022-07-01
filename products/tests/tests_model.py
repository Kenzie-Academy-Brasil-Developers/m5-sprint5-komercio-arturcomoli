import ipdb
from accounts.models import Account
from django.db import IntegrityError
from django.test import TestCase
from products.models import Product


class ProductModelTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:

        cls.seller = Account.objects.create(
            email="email@mail.com",
            first_name="John",
            last_name="Doe",
            is_seller=True,
        )

        cls.description = "Description teste"
        cls.price = 99.99
        cls.quantity = 15
        cls.is_active = False

        cls.product = Product(
            description=cls.description,
            price=cls.price,
            quantity=cls.quantity,
            is_active=cls.is_active,
        )

    def test_product_creation_attributes(self):
        self.product.seller = self.seller
        self.product.save()

        new_product = Product.objects.get(pk=1)

        self.assertEqual(self.product.description, new_product.description)
        self.assertEqual(self.product.price, new_product.price)
        self.assertEqual(self.product.quantity, new_product.quantity)
        self.assertEqual(self.product.is_active, new_product.is_active)
        self.assertIsInstance(self.product.seller, Account)

    def test_product_creation_without_seller(self):
        with self.assertRaises(IntegrityError):
            self.product.save()
