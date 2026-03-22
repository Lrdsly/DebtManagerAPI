from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

from users.models import MemberShip
# Enter your code here.

User = get_user_model()


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


class UserSerializer(PublicUserSerializer):
    
    class Meta:
        model = User
        exclude = ("room",)
        extra_kwargs = {
            **PublicUserSerializer.Meta.extra_kwargs,
        }

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")

        if not request.user.is_staff:
            exclude = ["user_permissions", "is_active", "is_staff", "is_superuser", "is_suspend"]
            for key in exclude:
                fields.pop(key)

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
