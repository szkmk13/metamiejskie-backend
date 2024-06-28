from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from metamiejskie.users.models import User, DailyQuest, Quest, DailyCoins, PatchNotes
from metamiejskie.permissions import IsYouOrReadOnly

from metamiejskie.users.serializers import (
    UserSerializer,
    DailyQuestSerializer,
    DailyQuestStartSerializer,
    QuestSerializer,
    PatchNotesSerializer,
)

from django.http import Http404

from allauth.account.models import (
    get_emailconfirmation_model,
)


class MetamiejskieConfirmEmailView(GenericAPIView):
    permission_classes = [AllowAny]

    def get_object(self, queryset=None):
        key = self.kwargs["key"]
        model = get_emailconfirmation_model()
        emailconfirmation = model.from_key(key)
        if not emailconfirmation:
            raise Http404()
        return emailconfirmation

    def post(self, *args, **kwargs):
        self.object = confirmation = self.get_object()
        email_address = confirmation.confirm(self.request)
        if not email_address:
            return Response("Email does not exist", status=404)
        user = confirmation.email_address.user
        user.is_active = True
        user.save()
        # return Response("ok")
        return Response({"detail": "Email confirmed"})


@extend_schema(tags=["patch notes"])
class PatchNotesView(ListModelMixin, GenericViewSet):
    permission_classes = [AllowAny]
    queryset = PatchNotes.objects.order_by("-date")
    serializer_class = PatchNotesSerializer


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

    @extend_schema(tags=["daily"], summary="Redeem daily coins")
    @action(detail=False, methods=["post"])
    def redeem_daily_coins(self, request):
        user = request.user
        if user.daily_coins_redeemed:
            return Response("Coins already redeemed", status=status.HTTP_400_BAD_REQUEST)
        DailyCoins.objects.create(user=user)
        user.refresh_from_db()
        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)


@extend_schema(tags=["daily"])
class DailyQuestViewSet(GenericViewSet):
    serializer_class = DailyQuestSerializer
    queryset = DailyQuest.objects.all()

    def get_queryset(self):
        return DailyQuest.objects.filter(user=self.request.user)  # type: ignore[misc]

    def get_serializer_class(self):
        if self.action == "start":
            return DailyQuestStartSerializer
        return DailyQuestSerializer

    @extend_schema(request=None, responses=QuestSerializer(many=True), summary="List of possible daily quests")
    @action(detail=False, methods=["get"], pagination_class=None)
    def choices(self, request):
        serializer = QuestSerializer(Quest.objects.all(), many=True, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @extend_schema(
        request=DailyQuestStartSerializer, responses={201: DailyQuestStartSerializer}, summary="Start a daily quest"
    )
    @action(detail=False, methods=["post"])
    def start(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(request=None, responses={200: str}, summary="Redeem reward from a daily quest")
    @action(detail=False, methods=["post"])
    def redeem(self, request):
        if request.user.tokens_redeemed():
            return Response("Rewards already redeemed", status=status.HTTP_400_BAD_REQUEST)
        now = timezone.now()
        qs = self.get_queryset().filter(created_at__date=now)
        if qs.count() == 0:
            return Response("No daily quest", status=status.HTTP_400_BAD_REQUEST)
        if qs.filter(will_end_at__gte=now).exists():
            return Response("Quest already started, wait for it to end", status=status.HTTP_400_BAD_REQUEST)
        request.user.redeem_from_quest(qs.first())
        return Response(status=status.HTTP_200_OK, data="Rewards redeemed")
