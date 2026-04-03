from rest_framework import serializers

from debts.models import Debt
# Enter your code here.


class DebtSerializer(serializers.ModelSerializer):
    status = serializers.CharField()
    debtor = serializers.CharField(source="debtor.username")
    creditor = serializers.CharField(source="creditor.username")
    room = serializers.CharField(source="room.slug")

    class Meta:
        model = Debt
        exclude = ("id",)

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        request = self.context.get("request")
        view = request.context.get("view")
        action = getattr(view, "action", None)

        if not action in ["retrieve"]:
            exclude = ["paied_at", "created_at", "description"]
            for key in exclude:
                fields.pop(key)
        
        return fields
