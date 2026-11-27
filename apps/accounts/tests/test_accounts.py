from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Role, User


class UserModelTests(TestCase):
    def test_default_role_is_patient(self):
        user = User.objects.create_user(username="jane", password="pw12345!")
        self.assertEqual(user.role, Role.PATIENT)
        self.assertTrue(user.is_patient)
        self.assertFalse(user.is_staff_role)

    def test_str_falls_back_to_username(self):
        user = User.objects.create_user(username="noNameUser", password="pw12345!")
        self.assertEqual(str(user), "noNameUser")


class SignUpViewTests(TestCase):
    def test_signup_creates_patient_account(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "newpatient",
                "first_name": "New",
                "last_name": "Patient",
                "email": "new.patient@example.com",
                "phone_number": "+919812345678",
                "password1": "S3cure!Passw0rd",
                "password2": "S3cure!Passw0rd",
            },
        )
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username="newpatient")
        self.assertEqual(user.role, Role.PATIENT)
