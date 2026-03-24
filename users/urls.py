from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import RoomView
# Enter your code here.

router = DefaultRouter()
router.register(r'rooms', RoomView, basename="rooms")

urlpatterns = [
    path('', include(router.urls)),    
]
