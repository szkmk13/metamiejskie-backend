from django.db.models import Count, Q

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status

from metamiejskie.meetings.models import Meeting, Place
from metamiejskie.meetings.serializers import (
    MeetingListSerializer,
    MeetingAddSerializer,
    PlaceSerializer,
)


@extend_schema(summary="Meetings view", tags=["meetings"])
class MeetingViewSet(
    viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin
):
    queryset = Meeting.objects.order_by("-date")

    def get_serializer_class(self):
        if self.action == "create":
            return MeetingAddSerializer
        if self.action == "places":
            return PlaceSerializer
        return MeetingListSerializer

    @extend_schema(summary="List of most used places", responses={200: PlaceSerializer(many=True)})
    @action(methods=["get"], detail=False)
    def places(self, request, *args, **kwargs):
        places = Place.objects.annotate(meetings_count=Count("meeting")).order_by("-meetings_count")
        return Response(self.get_serializer(places, many=True).data, status=status.HTTP_200_OK)

    @extend_schema(summary="List of meetings to confirm by you", responses={200: MeetingListSerializer(many=True)})
    @action(methods=["get"], detail=False)
    def to_confirm_by_you(self, request, *args, **kwargs):
        meetings_to_confirm = (
            self.queryset.annotate(confirmed_users=Count("attendance", filter=Q(attendance__confirmed=True))).filter(
                confirmed_users__lt=2
            )
        ).filter(Q(attendance__confirmed=False) & Q(attendance__user=request.user))

        serializer = self.get_serializer(meetings_to_confirm, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="List of meetings that wait to be confirmed by other users",
        responses={200: MeetingListSerializer(many=True)},
    )
    @action(methods=["get"], detail=False)
    def to_confirm_by_others(self, request, *args, **kwargs):
        meetings = self.queryset.annotate(confirmed_users=Count("attendance", filter=Q(attendance__confirmed=True)))
        meetings_confirmed_by_less_than_2_users = meetings.filter(confirmed_users__lt=2)
        less_than_2_confirmed_by_user = meetings_confirmed_by_less_than_2_users.filter(
            Q(attendance__user=request.user) & Q(attendance__confirmed=True)
        )

        serializer = self.get_serializer(less_than_2_confirmed_by_user, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.annotate(confirmed_users=Count("attendance", filter=Q(attendance__confirmed=True))).filter(
            confirmed_users__gte=2
        )
        serializer = self.get_serializer(queryset, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Confirm your attendance on meeting, by doing so gain coins and points",
        request=None,
        responses={200: str},
    )
    @action(methods=["post"], detail=True)
    def confirm(self, request, *args, **kwargs):
        meeting = self.get_object()
        user = request.user
        attendance = meeting.attendance_set.get(user=request.user)
        if attendance:
            if attendance.confirmed:
                return Response(data="You have already confirmed your attendance", status=status.HTTP_400_BAD_REQUEST)
            attendance.confirmed = True
            attendance.save(update_fields=["confirmed"])
            # todo find a way to block this from exploiting
            user.redeem_from_attendance()
            return Response("Confirmed")
        return Response(data="You weren't there", status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(summary="Decline your attendance on meeting", request=None, responses={200: str})
    @action(methods=["post"], detail=True)
    def decline(self, request, *args, **kwargs):
        meeting = self.get_object()
        user = request.user
        attendance = meeting.attendance_set.get(user=user)
        if attendance:
            if attendance.confirmed:
                return Response(data="You have already confirmed your attendance", status=status.HTTP_400_BAD_REQUEST)
            return Response(data="You confirmed that you weren't there", status=status.HTTP_200_OK)
        return Response(data="You weren't there", status=status.HTTP_400_BAD_REQUEST)
