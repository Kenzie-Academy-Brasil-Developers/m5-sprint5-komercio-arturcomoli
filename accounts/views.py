import ipdb
from rest_framework import generics, views
from rest_framework.authentication import TokenAuthentication, authenticate
from rest_framework.authtoken.models import Token
from rest_framework.views import Response, status

from accounts.exceptions import CannotUpdateKeyError
from accounts.permissions import AccountOwner, UpdateIsActive

from .models import Account
from .serializers import (
    AccountSerializer,
    LoginSerializer,
    ToggleIsActive,
    UpdateAccountSerializer,
)


class AccountView(generics.ListCreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class ListAccountsByGivenNum(generics.ListAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def get_queryset(self):
        max_accounts = self.kwargs["num"]
        return self.queryset.order_by("-date_joined")[0:max_accounts]


class UpdateAccountView(generics.UpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [AccountOwner]

    queryset = Account.objects.all()
    serializer_class = UpdateAccountSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_update(serializer)
        except CannotUpdateKeyError as err:
            return Response(
                {"detail": [str(err)]}, status.HTTP_400_BAD_REQUEST
            )

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class ToggleIsActiveView(generics.UpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [UpdateIsActive]

    queryset = Account.objects.all()
    serializer_class = ToggleIsActive

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_update(serializer)
        except CannotUpdateKeyError as err:
            return Response(
                {"detail": [str(err)]}, status.HTTP_400_BAD_REQUEST
            )

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    # def perform_update(self, serializer):
    #     ipdb.set_trace()
    #     try:
    #         serializer.save()
    #     except CannotUpdateKeyError as err:
    #         return Response({"detail": [str(err)]})
    #     serializer.save()
    #     return serializer.data


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
