from django.test import TestCase

# Create your tests here.


class Test(TestCase):
    def setUp(self) -> None:
        # login first
        self.client.post("/api/auth", {"email": "test@gmail.com", "password": "string"})
