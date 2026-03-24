from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login

from users.models import MemberShip, Room
from users.utils import counters
from debts.models import Debt
# Enter your code here.

User = get_user_model()


class RoomSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    members_property = serializers.SerializerMethodField()
    room_value = serializers.SerializerMethodField()
    mode = serializers.CharField()
    admin = serializers.CharField(source="admin.username")

    class Meta:
        model = Room
        exclude = ("id",)

    def get_fields(self):
        fields = super().get_fields()
        view = self.context.get("view")
        action = getattr(view, "action", None)

        if action == "list":
            exclude = ["members_property", "room_value", "created_at"]
            for key in exclude:
                fields.pop(key)

        elif action in ["update", "partial-update"]:
            allowed = ["name", "slug", "mode"]
            fields = {key:value for key,value in fields.items() if key in allowed}

        return fields

    def get_members_count(self, obj):
        return MemberShip.objects.filter(room=obj).count()

    def get_room_value(self, obj):
        room_value = counters.get_total_value(obj.slug)
        return room_value
    
    def get_members_property(self, obj):
        members = MemberShip.objects.filter(room=obj).values_list('user__username', flat=True)
        members_property = []
        for username in members:
            total_debt = counters.get_user_total_debt(obj.slug, username)
            members_property.append({
                "username": username,
                "totaol_debt": total_debt
            })
        return members_property


class RoomFilterSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, max_length=50)
