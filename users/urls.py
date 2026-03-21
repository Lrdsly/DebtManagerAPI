from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import UserView
# Enter your code here.

router = DefaultRouter()
router.register(r'api.users', UserView, basename="users")

urlpatterns = [
    path('', include(router.urls)),    
]
