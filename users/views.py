from django.shortcuts import render

from django.contrib.auth import get_user_model, login
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from users.serializers import *
# Create your views here.

User = get_user_model()


class UserView(ModelViewSet):
    queryset = User.objects.all()
    lookup_field = "username"
    # add autharation here later

    def get_serializer_context(self, **kwargs):
        context = super().get_serializer_context(**kwargs)
        context["is_staff"] = True if self.request.user.is_staff else False
        context["is_owner"] = True if self.request.user == self.get_object() else False
        return context
    
    def get_serializer_class(self):
        if self.request.user == self.get_object() or self.request.user.is_staff:
            return UserSerializer
        return PublicUserSerializer
