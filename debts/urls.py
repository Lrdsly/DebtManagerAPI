from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DebtView

# Enter your code here.

router = DefaultRouter()
router.register("debts", DebtView, basename="debts")

urlpatterns = [path("", include(router.urls))]
