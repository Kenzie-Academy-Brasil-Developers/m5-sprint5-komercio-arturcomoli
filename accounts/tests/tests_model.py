from accounts.models import Account
from django.test import TestCase
from django.utils import timezone


class AccountModelTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.email = "email@mail.com"
        cls.first_name = "John"
        cls.last_name = "Doe"
        cls.is_seller = True

        cls.account = Account.objects.create(
            email=cls.email,
            first_name=cls.first_name,
            last_name=cls.last_name,
            is_seller=cls.is_seller,
        )

    def test_model_atributtes(self):
        get_account = Account.objects.get(pk=1)
        self.assertEqual(self.account.email, get_account.email)
        self.assertEqual(self.account.first_name, get_account.first_name)
        self.assertEqual(self.account.last_name, get_account.last_name)
        self.assertEqual(self.account.is_seller, get_account.is_seller)
        self.assertFalse(get_account.is_superuser)
        self.assertTrue(get_account.is_active)
        self.assertIsNotNone("date_joined")
        self.assertIsNotNone("password")
