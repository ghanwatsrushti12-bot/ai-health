import datetime as dt

from django.test import TestCase
from django.urls import reverse

from apps.doctors.models import Department, Doctor, DoctorAvailability


class DoctorDirectoryTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Cardiology", slug="cardiology")
        self.doctor = Doctor.objects.create(
            full_name="Test Doctor",
            slug="test-doctor",
            department=self.department,
            designation="Consultant",
            qualifications="MBBS",
        )

    def test_department_doctor_count(self):
        self.assertEqual(self.department.doctor_count, 1)

    def test_doctor_list_view_returns_active_doctors(self):
        response = self.client.get(reverse("doctors:doctor_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Doctor")

    def test_inactive_doctor_hidden_from_public_list(self):
        self.doctor.is_active = False
        self.doctor.save()
        response = self.client.get(reverse("doctors:doctor_list"))
        self.assertNotContains(response, "Test Doctor")

    def test_doctor_detail_page(self):
        response = self.client.get(
            reverse("doctors:doctor_detail", kwargs={"slug": self.doctor.slug})
        )
        self.assertEqual(response.status_code, 200)


class DoctorAvailabilityConstraintTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="ENT", slug="ent")
        self.doctor = Doctor.objects.create(
            full_name="Slot Doctor",
            slug="slot-doctor",
            department=self.department,
            designation="Consultant",
            qualifications="MBBS",
        )

    def test_end_time_must_be_after_start_time(self):
        from django.db import IntegrityError, transaction

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DoctorAvailability.objects.create(
                    doctor=self.doctor,
                    weekday=0,
                    start_time=dt.time(10, 0),
                    end_time=dt.time(9, 0),
                )
