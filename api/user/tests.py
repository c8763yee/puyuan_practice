from django.test import TestCase


# Create your tests here.
class UserDateTest(TestCase):
    def setUp(self) -> None:
        # login first
        response = self.client.post(
            "/api/auth/login/", data={"email": "test@gmail.com", "password": "test"}
        )
        self.assertEqual(response.status_code, 200)
        self.token = response.json()["token"]

    def test_modify_user_info(self):
        response = self.client.patch(
            "/api/user/",
            data={"name": "test", "height": 180, "weight": 70},
            Authorization=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_get_user_info(self):
        response = self.client.get(
            "/api/user/",
            Authorization=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, 200)
        self.assertSetEqual(
            set(response.json().keys()),
            {"id", "default", "setting", "name", "height", "weight"},
        )
