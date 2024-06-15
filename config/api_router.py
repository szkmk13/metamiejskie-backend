from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from metamiejskie.casino.views import GameViewSet
from metamiejskie.chatbot.views import ChatBotViewSet
from metamiejskie.users.views import UserViewSet, DailyQuestViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("casino", GameViewSet)
router.register("quests", DailyQuestViewSet)
router.register("chatbot", ChatBotViewSet)

app_name = "api"
urlpatterns = router.urls
