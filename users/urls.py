from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import UserView, LoginView, RegisterView, NotificationView, RoomView
# Enter your code here.

router = DefaultRouter()
router.register(r'users', UserView, basename="users")
router.register(r'notifications', NotificationView, basename='notifications')
router.register(r'rooms', RoomView, basename="rooms")


urlpatterns = [
    path('', include(router.urls)),   
    path('users/login', LoginView.as_view(), name='login'),
    path('users/register', RegisterView.as_view(), name="register") 
]
