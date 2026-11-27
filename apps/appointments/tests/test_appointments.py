import datetime as dt

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.appointments.models import Appointment
from apps.appointments.services import get_available_slots
from apps.doctors.models import Department, Doctor, DoctorAvailability


class AvailableSlotsServiceTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Neurology", slug="neurology")
        self.doctor = Doctor.objects.create(
            full_name="Slot Doctor",
            slug="slot-doctor",
            department=self.department,
            designation="Consultant",
            qualifications="MBBS",
        )
        # Pick a fixed future Monday to keep the test deterministic.
        today = dt.date.today()
        days_ahead = (7 - today.weekday()) % 7 or 7
        self.monday = today + dt.timedelta(days=days_ahead)
        DoctorAvailability.objects.create(
            doctor=self.doctor,
            weekday=self.monday.weekday(),
            start_time=dt.time(9, 0),
            end_time=dt.time(10, 0),
            slot_minutes=20,
        )
        self.patient = User.objects.create_user(username="p1", password="pw12345!")

    def test_slots_generated_from_availability_window(self):
        slots = get_available_slots(self.doctor, self.monday)
        self.assertEqual(
            slots, [dt.time(9, 0), dt.time(9, 20), dt.time(9, 40)]
        )

    def test_booked_slot_is_excluded(self):
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            department=self.department,
            scheduled_date=self.monday,
            scheduled_time=dt.time(9, 0),
            reason="Checkup",
        )
        slots = get_available_slots(self.doctor, self.monday)
        self.assertNotIn(dt.time(9, 0), slots)

    def test_cancelled_appointment_frees_the_slot(self):
        appt = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            department=self.department,
            scheduled_date=self.monday,
            scheduled_time=dt.time(9, 20),
            reason="Checkup",
            status=Appointment.Status.CANCELLED,
        )
        slots = get_available_slots(self.doctor, self.monday)
        self.assertIn(dt.time(9, 20), slots)


class DoubleBookingConstraintTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="ENT", slug="ent-2")
        self.doctor = Doctor.objects.create(
            full_name="Busy Doctor",
            slug="busy-doctor",
            department=self.department,
            designation="Consultant",
            qualifications="MBBS",
        )
        self.patient_a = User.objects.create_user(username="pa", password="pw12345!")
        self.patient_b = User.objects.create_user(username="pb", password="pw12345!")
        self.date = dt.date.today() + dt.timedelta(days=3)

    def test_database_prevents_duplicate_active_bookings(self):
        Appointment.objects.create(
            patient=self.patient_a,
            doctor=self.doctor,
            department=self.department,
            scheduled_date=self.date,
            scheduled_time=dt.time(9, 0),
            reason="First booking",
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Appointment.objects.create(
                    patient=self.patient_b,
                    doctor=self.doctor,
                    department=self.department,
                    scheduled_date=self.date,
                    scheduled_time=dt.time(9, 0),
                    reason="Conflicting booking",
                )


class AppointmentAccessControlTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Ortho", slug="ortho")
        self.doctor = Doctor.objects.create(
            full_name="Access Doctor",
            slug="access-doctor",
            department=self.department,
            designation="Consultant",
            qualifications="MBBS",
        )
        self.owner = User.objects.create_user(username="owner", password="pw12345!")
        self.other = User.objects.create_user(username="other", password="pw12345!")
        self.appointment = Appointment.objects.create(
            patient=self.owner,
            doctor=self.doctor,
            department=self.department,
            scheduled_date=dt.date.today() + dt.timedelta(days=2),
            scheduled_time=dt.time(9, 0),
            reason="Checkup",
        )

    def test_patient_cannot_cancel_someone_elses_appointment(self):
        self.client.login(username="other", password="pw12345!")
        self.client.post(
            reverse("appointments:cancel", kwargs={"pk": self.appointment.pk})
        )
        self.appointment.refresh_from_db()
        self.assertNotEqual(self.appointment.status, Appointment.Status.CANCELLED)

    def test_owner_can_cancel_their_own_appointment(self):
        self.client.login(username="owner", password="pw12345!")
        self.client.post(
            reverse("appointments:cancel", kwargs={"pk": self.appointment.pk})
        )
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, Appointment.Status.CANCELLED)
