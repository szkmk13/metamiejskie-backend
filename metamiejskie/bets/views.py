from django.db.models import Count
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status

from metamiejskie.bets.models import Bet
from metamiejskie.bets.serializers import BetsListSerializer, BetVoteSerializer, VoteSerializer, CreateBetSerializer
from metamiejskie.meetings.models import Meeting, Place, Attendance


@extend_schema(summary="Bets view", tags=["bets"])
class BetsViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    queryset = Bet.objects.order_by("-deadline")
    serializer_classes = {
        "vote": BetVoteSerializer,
        "create": CreateBetSerializer,
        # "confirmed": ConfirmMeetingListSerializer,
        # "not_confirmed": ConfirmMeetingListSerializer,
        # "places": PlaceSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, BetsListSerializer)

    @extend_schema(summary="Vote for a bet", responses={201: VoteSerializer})
    @action(detail=True, methods=["post"])
    def vote(self, request, pk=None):
        bet = self.get_object()
        serializer = self.get_serializer(data=request.data, context={"request": request, "bet": bet})
        serializer.is_valid(raise_exception=True)
        vote_object = serializer.save()
        return Response(VoteSerializer(vote_object).data, status=status.HTTP_201_CREATED)
