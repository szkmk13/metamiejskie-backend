from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase, APIClient

from metamiejskie.meetings.models import Meeting
from metamiejskie.meetings.tests.factories import (
    MeetingWith1UserFactory,
    MeetingFactory,
    PlaceFactory,
    AttendanceFactory,
)
from metamiejskie.users.tests.factories import UserFactory, QuestFactory, DailyQuestFactory
from metamiejskie.utils import variables_setup


class TestMeetingModels(APITestCase):
    def setUp(self):
        variables_setup()
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_place_used_in_meeting(self):
        place = PlaceFactory()
        MeetingFactory(place=place)
        self.assertEqual(place.used_in_meetings, 1)
        self.assertEqual(place.__str__(), place.name)

    def test_attendance_str(self):
        meeting = MeetingFactory()
        attendance = AttendanceFactory(user=self.user, meeting=meeting)
        self.assertEqual(attendance.__str__(), f"{self.user} at {meeting}")

    def test_meeting_is_confirmed_by_users_false(self):
        meeting = MeetingFactory()
        self.assertEqual(meeting.is_confirmed_by_users, False)

    def test_meeting_is_confirmed_by_users_true(self):
        meeting = MeetingFactory()
        AttendanceFactory(meeting=meeting, confirmed=True)
        AttendanceFactory(meeting=meeting, confirmed=True)
        AttendanceFactory(meeting=meeting, confirmed=True)
        self.assertEqual(meeting.is_confirmed_by_users, True)

    def test_meeting_count_attendance(self):
        self.assertEqual(Meeting.count_attendance(self.user), 0)

    def test_meeting_how_many_attended(self):
        meeting = MeetingFactory()
        self.assertEqual(meeting.how_many_attended, 0)

    def test_meeting_confirmed_by_less_than_2_users(self):
        meeting = MeetingFactory()
        AttendanceFactory(meeting=meeting, confirmed=True)
        self.assertEqual(meeting.confirmed_by_less_than_2_users, True)

    def test_meeting_confirmed_by_user_false(self):
        meeting = MeetingFactory()
        AttendanceFactory(user=self.user, meeting=meeting)
        self.assertEqual(meeting.confirmed_by_user(self.user), False)

    def test_meeting_confirmed_by_user_true(self):
        meeting = MeetingFactory()
        AttendanceFactory(user=self.user, meeting=meeting, confirmed=True)
        self.assertEqual(meeting.confirmed_by_user(self.user), True)
