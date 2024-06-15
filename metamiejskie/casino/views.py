from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from metamiejskie.casino.models import Game
from metamiejskie.casino.serializers import GameSerializer, GameSpinSerializer, SpinResultSerializer


# Create your views here.


@extend_schema(tags=["casino WORK IN PROGRESS"])
class GameViewSet(ListModelMixin, GenericViewSet):
    queryset = Game.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "spin":
            return GameSpinSerializer
        return GameSerializer

    def get_queryset(self):
        print(self.request.user)
        return Game.objects.all()

    @extend_schema(summary="Get list of possible games")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        request=GameSpinSerializer,
        responses={200: SpinResultSerializer},
        summary="""Provide id of the game and play it""",
    )
    @action(methods=["post"], detail=True)
    def spin(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = self.get_object()
        result = SpinResultSerializer(obj.run(self.request.user, serializer.validated_data["lines_chosen"]))
        print(obj)
        return Response(result.data)
