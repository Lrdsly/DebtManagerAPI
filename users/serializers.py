from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login

from users.models import MemberShip, Room, Notification
from users.utils import counters
from debts.models import Debt
# Enter your code here.

User = get_user_model()

# why should password and... be exists (in any type of ro, wo etc) in public serializer
class PublicUserSerializer(serializers.ModelSerializer):
    joined_rooms = serializers.SerializerMethodField()
    rooms = serializers.SerializerMethodField()
    last_login = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()


    class Meta:
        model = User
        fields = ("name", "username", "status", "joined_rooms", "rooms", "last_login", "date_joined")
        extra_kwargs = {
            "password": {"write_only": True},
            "date_joined": {"read_only": True},
            "last_login": {"read_only": True}
        }
    
    def get_joined_rooms(self, obj):
        return MemberShip.objects.filter(user=obj).count()
    
    def get_rooms(self, obj):
        return MemberShip.objects.filter(user=obj).values_list("room_id__name", flat=True)
    
    def get_last_login(self, obj):
        if not obj.last_login:
            return "Never logged before"
        return obj.last_login
    
    def get_status(self, obj):
        if obj.is_staff:
            return "admin"
        elif obj.is_premium:
            return "premium account"
        return "normal user"
    

class UserSerializer(PublicUserSerializer):
    # total_debt 

    class Meta:
        model = User
        exclude = ("room",)
        extra_kwargs = {
            **PublicUserSerializer.Meta.extra_kwargs,
        }

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        view = self.context.get("view")
        action = getattr(view, "action", None)

        if not request.user.is_staff:

            if action == "list":
                allowed = ["name", "username", "joined_rooms", "status"]
            elif action == "retrieve":
                allowed = ["name", "username", "joined_rooms", "rooms", "status", "last_login", "created_at"]
            elif action in ["update", "partial_update"]:
                # where should I add password change?
                allowed = ["name", "username"]
            fields = {key: value for key, value in fields.items() if key in allowed}

        elif request.user.is_staff: # staff permissions
            
            if action == "list":
                allowed = ["name", "username", "joined_rooms", "status"]
            elif action == "retrieve":
                allowed = ["name", "username", "joined_rooms", "rooms", "lost_login", "created_at",
                            "is_premium", "is_staff", "is_superuser", "is_suspend", "user_permissions"]
            elif action in ["update", "partial_update"]:
                allowd = ["is_suspend", "is_premium"]
                if request.user.is_superuser:
                    allowed.append("is_staff")
            fields = {key: value for key, value in fields.items() if key in allowed}

        return fields


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request = self.context.get("request")

        user = authenticate(request, 
                            username=attrs.get("username"),
                            password=attrs.get("password"))
        if not user:
            raise serializers.ValidationError("username of password is not correct.")
        attrs["user"] = user
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    repassword = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = ("name", "username", "password", "repassword")
        extra_kwargs = {
            "name": {"required": False}
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)
  
        if attrs.get("password") != attrs.get("repassword"):
            raise serializers.ValidationError("passwords didn't match correct.")
        
        return super().validate(attrs)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_new_password = serializers.CharField()

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_new_password"]:
            raise serializers.ValidationError("Password didn't match.")
        return attrs


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        exclude = ("id",)


class RoomSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    members_property = serializers.SerializerMethodField()
    room_value = serializers.SerializerMethodField()
    mode = serializers.CharField()
    admin = serializers.CharField(source="admin.username")

    class Meta:
        model = Room
        exclude = ("id",)

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
