import datetime
import json

import requests
from dateutil.parser import isoparse
from django.db.models import Count, Q, Case, When
from django.shortcuts import render
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import viewsets, mixins, permissions, status

from config import settings
from metamiejskie.meetings.models import Meeting, Attendance
from metamiejskie.meetings.serializers import (
    MeetingListSerializer,
    MeetingDetailSerializer,
    MeetingAddSerializer,
    AttendanceSerializer,
)

from metamiejskie.permissions import IsYouOrReadOnly
from metamiejskie.users.models import User


# Create your views here.
class MeetingViewSet(
    viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin
):
    """
    API endpoint that returns meetings data

    you can add meeting with post method
    """

    queryset = Meeting.objects.all().order_by("-date")
    serializer_class = MeetingListSerializer

    permission_classes = [IsYouOrReadOnly, permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        date_wrong = data["date"]
        # Parse the string into a datetime object
        original_datetime = isoparse(date_wrong)
        # Add 3 hours
        new_datetime = original_datetime + datetime.timedelta(hours=3)
        # Get the date
        data["date"] = new_datetime.date()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return MeetingDetailSerializer
        if self.action == "create":
            return MeetingAddSerializer
        return MeetingListSerializer

    @action(methods=["get"], detail=False)
    def places(self, request, *args, **kwargs):
        """
        Lists dostępne places of meetings

        xd
        """
        return Response([place[0] for place in Meeting.PLACES])

    @action(methods=["get"], detail=False)
    def pending(self, request, *args, **kwargs):
        """
        list of unconfirmed metings

        mniej niz 2 osoby i ty nie potwierdziles
        """
        user = User.objects.get(user=request.user)
        meetings = (
            Meeting.objects.annotate(confirmed_users=Count("attendance", filter=Q(attendance__confirmed=True)))
            .filter(confirmed_users__lt=2)
            .annotate(user_was_there=Count("attendance", filter=Q(attendance__user=user)))
            .filter(user_was_there=1)
            .order_by("-date")
        )

        new_qs = meetings

        for _ in meetings:
            if Attendance.objects.get(meeting=_, user=user).confirmed:
                if _.user_was_there == 1:
                    new_qs = new_qs.exclude(id=_.id)

        qs = new_qs  # if new_qs else meetings
        serializer = MeetingListSerializer(qs, many=True, context={"request": request})
        return Response(
            serializer.data,
        )

    @action(methods=["get"], detail=False)
    def waiting(self, request, *args, **kwargs):
        """
        list of metings that are confirmed by you but not by someone else

        mniej niz 2 osoby i ty juz potwierdziles
        """
        user = User.objects.get(user=request.user)

        meetings = Meeting.objects.all().order_by("-date")
        meetings_confirmed_by_less_than_2_users = meetings
        for meeting in meetings:
            if not meeting.confirmed_by_less_than_2_users:
                meetings_confirmed_by_less_than_2_users = meetings_confirmed_by_less_than_2_users.exclude(id=meeting.id)
        less_than_2_confirmed_by_user = meetings_confirmed_by_less_than_2_users
        for meeting in meetings_confirmed_by_less_than_2_users:
            if not meeting.confirmed_by_user(user):
                less_than_2_confirmed_by_user = less_than_2_confirmed_by_user.exclude(id=meeting.id)

        serializer = MeetingListSerializer(less_than_2_confirmed_by_user, many=True, context={"request": request})
        return Response(
            serializer.data,
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.annotate(confirmed_users=Count("attendance", filter=Q(attendance__confirmed=True))).filter(
            confirmed_users__gte=2
        )
        serializer = self.get_serializer(queryset, many=True, context={"request": request})
        return Response(
            serializer.data,
        )

    @action(methods=["get"], detail=True)
    def confirm(self, request, *args, **kwargs):
        """
        Potwierdza Twoją obecność na meetingu

        xd
        """
        meeting = self.get_object()
        user = User.objects.get(user=request.user)
        attendance = meeting.attendance_set.get(user=user)
        if attendance:
            if attendance.confirmed:
                return Response(status=400, data="Już potwierdziłeś swoją obecność")
            attendance.confirmed = True
            attendance.save()
            return Response("Potwierdzono")
        return Response(status=400, data="Nie było Cię tam")

    @action(methods=["get"], detail=True)
    def decline(self, request, *args, **kwargs):
        """
        nie Potwierdza Twoją obecność na meetingu

        xd
        """
        meeting = self.get_object()
        user = User.objects.get(user=request.user)
        attendance = meeting.attendance_set.get(user=user)
        if attendance:
            if attendance.confirmed:
                return Response(status=400, data="Już potwierdziłeś swoją obecność")
            return Response("Potwierdziłeś że Cię tam nie było, o co Ci właściwie chodzi koleś")
        return Response(status=400, data="Nie było Cię tam")
