from django.utils import timezone
from django.views.generic.base import RedirectView
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from django.conf import settings
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from metamiejskie.users.models import User, DailyQuest, Quest, DailyCoins
from metamiejskie.users.permissions import IsYouOrReadOnly

from metamiejskie.users.serializers import (
    UserSerializer,
    DailyQuestSerializer,
    DailyQuestStartSerializer,
    QuestSerializer,
)


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsYouOrReadOnly]

    def get_queryset(self):
        return User.objects.all()

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=False, methods=["post"])
    def redeem_daily_coins(self, request):
        user = request.user
        if user.daily_coins_redeemed:
            return Response("Coins already redeemed", status=status.HTTP_400_BAD_REQUEST)
        DailyCoins.objects.create(user=user)
        user.refresh_from_db()
        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)


class DailyQuestViewSet(GenericViewSet):
    serializer_class = DailyQuestSerializer
    queryset = DailyQuest.objects.all()

    def get_queryset(self):
        return DailyQuest.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "start":
            return DailyQuestStartSerializer
        return DailyQuestSerializer

    @extend_schema(request=DailyQuestStartSerializer, responses={200: str})
    @action(detail=False, methods=["post"])
    def start(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(request=None, responses={200: str})
    @action(detail=False, methods=["post"])
    def redeem(self, request):
        if request.user.tokens_redeemed():
            return Response("Tokens already redeemed", status=status.HTTP_400_BAD_REQUEST)
        now = timezone.now()
        qs = self.get_queryset().filter(created_at__date=now)
        if qs.count() == 0:
            return Response("No daily quest", status=status.HTTP_400_BAD_REQUEST)
        if qs.filter(will_end_at__gte=now).exists():
            return Response("Quest already started, wait for it to end", status=status.HTTP_400_BAD_REQUEST)
        request.user.redeem_from_quest(qs.first())
        return Response(status=status.HTTP_200_OK, data="Tokens redeemed")

    @extend_schema(request=None, responses=QuestSerializer(many=True))
    @action(detail=False, methods=["get"], pagination_class=None)
    def choices(self, request):
        serializer = QuestSerializer(Quest.objects.all(), many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
