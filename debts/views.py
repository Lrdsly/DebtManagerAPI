from django.shortcuts import render
from django.contrib.auth import get_user_model

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from debts.models import Debt, StatusDebt
from debts.serializers import DebtSerializer
from debts.utils import permissions
# Create your views here.


class DebtView(ModelViewSet):
    queryset = Debt.objects.all()
    serializer_class = DebtSerializer

    def get_serializer_context(self):
        context =  super().get_serializer_context()
        context["view"] = self
        return context

    def get_permissions(self):
        if self.action in ["confirm", "reject", "pay", "confirm_payment"]:
            if self.action in ["confirm", "reject", "paied"]:
                permission_classes = [permissions.IsCreditor]
            elif self.action in ["confirm_payment"]:
                permission_classes = [permissions.IsDebtor]        
        elif self.action in ["list", "retrieve"]:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def _perform_transition_action(self, expect_status:StatusDebt, new_status:StatusDebt, user, success_message:str, error_message:str):
        debt = self.get_object()
        if debt.status == expect_status:
            final_status = debt.change_status(new_status, self.request.user)
            response = {"message": success_message}
            if final_status != new_status:
                response["PS"] = f"Your intended status was '{new_status}', but according to system logic, it has been automatically updated to '{final_status}'."
            return Response(response, status=status.HTTP_200_OK)
        return Response({"message": error_message}, status=status.HTTP_406_NOT_ACCEPTABLE)
    
    @action("post", detail=True, url_path="confirm")
    def confirm(self, request):
        self._perform_transition_action(StatusDebt.PENDING, StatusDebt.CONFIRMED, self.request.user,
                                        "debt confirmed successfully.", "you can not change this status to confirmed")

    @action("post", detail=True, url_path="reject")
    def reject(self, request):
        self._perform_transition_action(StatusDebt.PENDING, StatusDebt.REJECTED, self.request.user,
                                        "debt rejected successfully.", "you can not change this status to rejected.") 

    @action("post", detail=True, url_path="pay")
    def pay(self, request):
        self._perform_transition_action(StatusDebt.CONFIRMED, StatusDebt.PAIED, self.request.user,
                                        "debt status updated to paied.", "you can not change this status to paied.")

    @action("post", detail=True, url_path="confirm_payment")
    def confirm_payment(self, request):
        self._perform_transition_action(StatusDebt.PAIED, StatusDebt.PAYCONFIRMED, self.request.user,
                                        "payment confirmed successfully.", "you can not confirm the debt payment yet.")
    
    def update(self, request, *args, **kwargs):
        return Response({"error": "You can not update debt objects using this action. Use declared actions insted."},
                 status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def partial_update(self, request, *args, **kwargs):
        return Response({"error": "You can not update debt objects using this action. Use declared actions insted."},
                 status=status.HTTP_405_METHOD_NOT_ALLOWED)
