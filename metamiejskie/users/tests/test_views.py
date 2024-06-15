from rest_framework.test import APITestCase, APIClient

from metamiejskie.users.tests.factories import UserFactory


class TestUserViewSet(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_claim_daily_coins(self):
        coins_before = self.user.coins
        response = self.client.post("/api/users/redeem_daily_coins/")
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.coins, coins_before + 10)

    def test_claim_daily_coins_redeem_second_time(self):
        response = self.client.post("/api/users/redeem_daily_coins/")
        self.assertEqual(response.status_code, 200)
        response = self.client.post("/api/users/redeem_daily_coins/")
        self.assertEqual(response.status_code, 400)
