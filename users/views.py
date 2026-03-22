from django.shortcuts import render

from django.contrib.auth import get_user_model, login
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from users.serializers import *
# Create your views here.

User = get_user_model()


class UserView(ModelViewSet):
    queryset = User.objects.all()
    lookup_field = "username"
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.user == self.get_object() or self.request.user.is_staff:
            return UserSerializer
        return PublicUserSerializer


class LoginView(APIView):
    http_method_names = ["post"]
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            login(request, serializer.validated_data.get("user"))
            return Response(status=status.HTTP_200_OK, data={"Messagee": "you logged in successfully.",
                                                             "username": serializer.validated_data.get('username')})
        return Response(serializer.error_messages)

# Add login rate limit later
class RegisterView(APIView):
    permission_classes = [~IsAuthenticated]
    http_method_names = ["post"]
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data) 
        if serializer.is_valid():
            v = serializer.validated_data
            user = User.objects.create_user(username=v["username"], password=v["password"], name=v.get("name", v["username"]))
            login(request, user)
            return Response(data={"message": "user created successfully.",
                                "username": v["username"]},
                                status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
