from django.urls import include, path
from rest_framework.routers import DefaultRouter

from core.views import UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
