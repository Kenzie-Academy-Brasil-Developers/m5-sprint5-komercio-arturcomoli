import ipdb
from accounts.models import Account
from accounts.serializers import AccountSerializer
from black import assert_equivalent
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework.views import status


class AccountTestView(APITestCase):
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
        cls.user_not_seller = {
            "email": "jane@doe.com",
            "password": "abcd",
            "first_name": "Jane",
            "last_name": "Doe",
            "is_seller": False,
        }

        cls.accounts = [
            Account.objects.create_user(
                email=f"email{user_id}",
                password="abcd",
                first_name=f"Name {user_id}",
                last_name=f"Surname {user_id}",
                is_seller=False,
            )
            for user_id in range(1, 10)
        ]

    def test_seller_creation(self):
        response = self.client.post("/api/accounts/", data=self.user_seller)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["is_seller"], self.user_seller["is_seller"]
        )
        self.assertNotIn("password", response.data)
        self.assertIn("date_joined", response.data)

    def test_not_seller_creation(self):
        response = self.client.post(
            "/api/accounts/", data=self.user_not_seller
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["is_seller"], self.user_not_seller["is_seller"]
        )
        self.assertNotIn("password", response.data)
        self.assertIn("date_joined", response.data)

    def test_wrong_keys_creation(self):
        response = self.client.post(
            "/api/accounts/", data={"is_seller": "teste"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("password", response.data)
        self.assertIn("first_name", response.data)
        self.assertIn("last_name", response.data)
        self.assertIn("is_seller", response.data)
        self.assertIn("boolean", str(response.data["is_seller"]))

    def test_duplicated_email(self):
        self.client.post("/api/accounts/", data=self.user_not_seller)
        response = self.client.post(
            "/api/accounts/", data=self.user_not_seller
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("already exists", str(response.data["email"]))

    def test_login_success_seller(self):
        user = Account.objects.create_user(**self.user_seller)

        response = self.client.post("/api/login/", data=self.user_seller)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.auth_token.key, response.data["token"])

    def test_login_success_not_seller(self):
        user = Account.objects.create_user(**self.user_not_seller)

        response = self.client.post("/api/login/", data=self.user_not_seller)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.auth_token.key, response.data["token"])

    def test_only_owner_can_update(self):
        user_owner = Account.objects.create_user(**self.user_seller)
        token = Token.objects.create(user=user_owner)
        user_not_owner = Account.objects.create_user(**self.user_not_seller)
        wrong_token = Token.objects.create(user=user_not_owner)

        self.client.credentials(HTTP_AUTHORIZATION="Token " + wrong_token.key)
        response = self.client.patch(
            f"/api/accounts/{user_owner.id}/", data={"email": "test@mail.com"}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_updating_success(self):
        data_patch = {"email": "teste@mail.com", "password": "1234"}

        user_owner = Account.objects.create_user(**self.user_seller)
        token = Token.objects.create(user=user_owner)

        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        response = self.client.patch(
            f"/api/accounts/{user_owner.id}/", data=data_patch
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], data_patch["email"])
        # self.assertEqual(
        #     response.data["date_joined"], str(user_owner.date_joined)
        # )
        self.assertNotIn("password", response.data)

    def test_trying_to_toggle_is_active_common_user(self):
        user = Account.objects.create_user(**self.user_seller)
        token = Token.objects.create(user=user)

        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        response = self.client.patch(
            f"/api/accounts/{user.id}/management/", data={"is_active": False}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_only_admin_can_deactive_account(self):
        user = Account.objects.create_superuser(**self.user_admin)
        token = token = Token.objects.create(user=user)

        common_user = Account.objects.create_user(**self.user_seller)

        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        data_patch = {"is_active": False}

        response = self.client.patch(
            f"/api/accounts/{common_user.id}/management/",
            data=data_patch,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_active"], data_patch["is_active"])

    def test_only_admin_can_activate_account(self):
        user = Account.objects.create_superuser(**self.user_admin)
        token = token = Token.objects.create(user=user)

        common_user = Account.objects.create_user(**self.user_seller)

        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        data_patch = {"is_active": True}

        response = self.client.patch(
            f"/api/accounts/{common_user.id}/management/",
            data=data_patch,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_active"], data_patch["is_active"])

    def test_anyone_can_list_users(self):

        response = self.client.get("/api/accounts/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.accounts))

        for account in self.accounts:
            self.assertIn(
                AccountSerializer(instance=account).data, response.data
            )
