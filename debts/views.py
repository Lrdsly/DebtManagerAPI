from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet

from debts.models import Debt
from debts.serializers import DebtSerializer
# Create your views here.

class DebtView(ModelViewSet):
    queryset = Debt.objects.all()
    serializer_class = DebtSerializer

    def get_serializer_context(self):
        context =  super().get_serializer_context()
        context["view"] = self
        return context
