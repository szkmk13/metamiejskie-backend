from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from metamiejskie.bets.views import BetsViewSet
from metamiejskie.casino.views import CasinoViewSet, CardGameViewSet
from metamiejskie.chatbot.views import ChatBotViewSet
from metamiejskie.meetings.views import MeetingViewSet
from metamiejskie.users.views import UserViewSet, DailyQuestViewSet, PatchNotesView

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("casino", CasinoViewSet, basename="casino")
router.register("quests", DailyQuestViewSet)
router.register("chatbot", ChatBotViewSet)
router.register("meetings", MeetingViewSet)
router.register("bets", BetsViewSet)

app_name = "api"

urlpatterns = [
    path("patch_notes/", PatchNotesView.as_view({"get": "list"}), name="patch-notes"),
    path("", include(router.urls)),
]
