from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import Student


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


User = get_user_model()


class ProfileTest(APITestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
        )
        self.student_data = {
            "birth_date": "1995-05-15",
            "education": "PHD",
            "phone_number": "+123456789",
        }
        self.student = Student.objects.create(user=self.user, **self.student_data)

    def test_unauthenticated_get(self):
        url = reverse("profile")
        response = self.client.get(path=url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_get(self):
        url = reverse("profile")
        token = get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token["access"]}')
        response = self.client.get(path=url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "first_name": "Test",
                "last_name": "User",
                "student": {
                    "birth_date": "1995-05-15",
                    "education": "PHD",
                    "phone_number": "+123456789",
                },
            },
        )

