from rest_framework import serializers

from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q

from users.models import MemberShip, Notification, FriendShip
# Enter your code here.

User = get_user_model()

# why should password and... be exists (in any type of ro, wo etc) in public serializer
class PublicUserSerializer(serializers.ModelSerializer):
    joined_rooms = serializers.SerializerMethodField()
    rooms = serializers.SerializerMethodField()
    last_login = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    friends = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("name", "username", "status", "joined_rooms", "rooms", "last_login", "date_joined", "friends")
        extra_kwargs = {
            "password": {"write_only": True},
            "date_joined": {"read_only": True},
            "last_login": {"read_only": True}
        }
    
    def get_fields(self):
        fields = super().get_fields()
        view = self.context.get("view")
        action = getattr(view, "action", None)

        if action == "list":
            allowed = {"name", "username", "joined_room"}
            fields = {name: field for name,field in fields.items() if name in allowed}
        if action == "retrieve":
            pass

        return fields
 
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
    
    def get_friends(self, obj):
        friendships = FriendShip.objects.filter(Q(user1=obj) | Q(user2=obj))
        friends = [f.user2.username if f.user1 == obj else f.user1.username for f in friendships]
        return friends


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


        if action == "list":
                allowed = ["name", "username", "joined_rooms", "status"]
        elif action == "retrieve":
                allowed = ["name", "username", "joined_rooms", "rooms", "status", "last_login", "created_at"]
        
        if not request.user.is_staff: # user own
            if action in ["update", "partial_update"]:
                # where should I add password change?
                allowed = ["name", "username"]
            fields = {key: value for key, value in fields.items() if key in allowed}

        elif request.user.is_staff: # staff permissions
            if action == "retrieve":
                # allowed initialized before in top conditions
                allowed.extend(["is_premium", "is_staff", "is_superuser", "is_suspend", "user_permissions"])
            elif action in ["update", "partial_update"]:
                allowed = ["is_suspend", "is_premium"]
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
