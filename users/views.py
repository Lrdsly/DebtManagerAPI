from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth import get_user_model

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from users.serializers import *
from users.utils import permissions as cp
from debts.serializers import DebtSerializer
# Create your views here.

User = get_user_model()


class RoomView(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    lookup_field = "slug"

    @action("list", detail=True, url_path="debts")
    def debts_list(self, request): 
        room = self.get_object()

        if request.query_params is not None:
            filters = RoomFilterSerializer(data=request.query_params)
            if filters.is_valid():
                try:
                    user = User.objects.get(username=filters.validated_data["username"])
                    debts = Debt.objects.filter(Q(room=room) & (Q(debtor=user) | Q(creditor=user)))
                    debt_serializer = DebtSerializer(instance=debts, many=True)
                    return Response(debt_serializer.data, status=status.HTTP_200_OK)
                
                except User.DoesNotExist:
                    return Response({"detail": "user not found."})
                
            return Response(filters.errors, status=status.HTTP_400_BAD_REQUEST)
        
        debts = Debt.objects.filter(room=room)
        debt_serializer = DebtSerializer(instance=debts, many=True)
        return Response(debt_serializer.data, status=status.HTTP_200_OK)
            
    def get_serializer_context(self):
        context =  super().get_serializer_context()
        context["view"] = self
        return context

    def get_permissions(self):
        if self.action in ["retrieve", "debt_list"]:
            permission_classes = [cp.IsMember]
        
        elif self.action == "list":
            permission_classes = [IsAuthenticated]
        
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [cp.IsRoomAdmin]
        
        return [permission() for permission in permission_classes]
