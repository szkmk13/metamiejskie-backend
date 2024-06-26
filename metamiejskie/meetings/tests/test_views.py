from datetime import timedelta
from time import sleep

from django.utils import timezone
from rest_framework.test import APITestCase, APIClient

from metamiejskie.meetings.tests.factories import PlaceFactory
from metamiejskie.users.tests.factories import UserFactory, QuestFactory, DailyQuestFactory


class TestMeetingsViewset(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.place = PlaceFactory()

    def test_places(self):
        response = self.client.get("/api/meetings/places/")
        self.assertEqual(len(response.data), 1)
    def test_meetings_list_no_meetings(self):
        response = self.client.get("/api/meetings/")
        self.assertEqual(len(response.data), 0)
    def test_meetings_list_1_confirmed_meeting(self):
        response = self.client.get("/api/meetings/")
        self.assertEqual(len(response.data), 0)
