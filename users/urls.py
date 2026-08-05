from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import LoginView, NotificationView, RegisterView, RoomView, UserView

# Enter your code here.

router = DefaultRouter()
router.register(r"users", UserView, basename="users")
router.register(r"rooms", RoomView, basename="rooms")

urlpatterns = [
    path("", include(router.urls)),
    path("users/login", LoginView.as_view(), name="login"),
    path("users/register", RegisterView.as_view(), name="register"),
    path("notifications/", NotificationView.as_view(), name="notifications"),
    path(
        "notifications/<int:pk>/",
        NotificationView.as_view(),
        name="notifications_update",
    ),
]
