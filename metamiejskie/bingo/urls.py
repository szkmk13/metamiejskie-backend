from rest_framework import routers

from metamiejskie.bingo.views import BingoViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from metamiejskie.bingo.views import BingoGetOrCreateAPIView

router = routers.DefaultRouter()
router.register("", BingoViewSet)


urlpatterns = [
    path("bingo/", BingoGetOrCreateAPIView.as_view(), name="bingo"),
    path("bingos/", include(router.urls), name="bingo"),
]
