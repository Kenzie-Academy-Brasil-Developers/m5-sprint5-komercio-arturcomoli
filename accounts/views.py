from rest_framework import generics, views
from rest_framework.authentication import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.views import Response, status

from .models import Account
from .serializers import AccountSerializer, LoginSerializer


class AccountView(generics.ListCreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class ListAccountsByGivenNum(generics.ListAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_queryset(self):
        max_accounts = self.kwargs["num"]
        return self.queryset.order_by("-date_joined")[0:max_accounts]


class LoginView(views.APIView):
    def post(self, request):

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})

        return Response(
            {"detail": "invalid email or password"},
            status.HTTP_401_UNAUTHORIZED,
        )
