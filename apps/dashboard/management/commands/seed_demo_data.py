"""Populates the database with realistic demo data for local development
and screenshots.

Usage:
    python manage.py seed_demo_data
    python manage.py seed_demo_data --flush   # wipe demo data first
"""

from __future__ import annotations

import datetime as dt
import random

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.accounts.models import Role, User
from apps.ambulance.models import AmbulanceRequest
from apps.appointments.models import Appointment
from apps.doctors.models import Department, Doctor, DoctorAvailability
from apps.feedback.models import Feedback
from apps.triage.models import Condition, Symptom

DEPARTMENTS = [
    ("Cardiology", "bi-heart-pulse", "Heart health, ECG, and cardiac rehabilitation."),
    ("Pediatrics", "bi-emoji-smile", "Comprehensive care for infants, children, and teens."),
    ("Orthopedics", "bi-bandaid", "Bones, joints, ligaments, and sports injuries."),
    ("Neurology", "bi-cpu", "Brain, spine, and nervous system disorders."),
    ("Gynecology", "bi-flower1", "Women's health, prenatal, and obstetric care."),
    ("Dermatology", "bi-droplet", "Skin, hair, and nail conditions."),
    ("General Medicine", "bi-clipboard2-pulse", "Everyday illnesses and preventive checkups."),
]

DOCTORS = [
    ("Ananya Sharma", "Cardiology", "Senior Consultant Cardiologist", "MBBS, MD, DM (Cardiology)", 14),
    ("Rohan Deshpande", "Cardiology", "Interventional Cardiologist", "MBBS, MD, DM", 9),
    ("Meera Iyer", "Pediatrics", "Senior Pediatrician", "MBBS, MD (Pediatrics)", 12),
    ("Kabir Nair", "Pediatrics", "Consultant Pediatrician", "MBBS, DCH", 6),
    ("Sandeep Kulkarni", "Orthopedics", "Senior Orthopedic Surgeon", "MBBS, MS (Ortho)", 16),
    ("Priya Rao", "Neurology", "Consultant Neurologist", "MBBS, MD, DM (Neurology)", 10),
    ("Arjun Menon", "Gynecology", "Senior Gynecologist", "MBBS, MS (Obs & Gyn)", 13),
    ("Sneha Kapoor", "Dermatology", "Consultant Dermatologist", "MBBS, MD (Dermatology)", 7),
    ("Vikram Singh", "General Medicine", "Senior Physician", "MBBS, MD (Medicine)", 18),
    ("Isha Bhat", "General Medicine", "Consultant Physician", "MBBS, MD", 5),
]

SYMPTOMS = [
    "fever", "cough", "headache", "sore_throat", "fatigue", "nausea",
    "vomiting", "chest_pain", "shortness_of_breath", "dizziness",
    "skin_rash", "joint_pain", "abdominal_pain", "diarrhea", "chills",
    "loss_of_appetite", "muscle_ache", "runny_nose", "palpitations",
    "back_pain",
]

CONDITIONS = [
    ("Common Cold", ["cough", "sore_throat", "runny_nose", "fatigue"], Condition.Severity.LOW, "General Medicine"),
    ("Influenza", ["fever", "chills", "muscle_ache", "fatigue", "headache"], Condition.Severity.MODERATE, "General Medicine"),
    ("Migraine", ["headache", "dizziness", "nausea"], Condition.Severity.MODERATE, "Neurology"),
    ("Gastroenteritis", ["nausea", "vomiting", "diarrhea", "abdominal_pain"], Condition.Severity.MODERATE, "General Medicine"),
    ("Angina", ["chest_pain", "shortness_of_breath", "palpitations", "fatigue"], Condition.Severity.HIGH, "Cardiology"),
    ("Acute Arthritis Flare", ["joint_pain", "fatigue", "muscle_ache"], Condition.Severity.MODERATE, "Orthopedics"),
    ("Allergic Skin Reaction", ["skin_rash", "fatigue"], Condition.Severity.LOW, "Dermatology"),
    ("Possible Cardiac Emergency", ["chest_pain", "shortness_of_breath", "dizziness", "palpitations"], Condition.Severity.EMERGENCY, "Cardiology"),
]


class Command(BaseCommand):
    help = "Seed the database with demo departments, doctors, symptoms, conditions, and sample activity."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete previously seeded demo data before re-creating it.",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self._flush()

        departments = self._seed_departments()
        doctors = self._seed_doctors(departments)
        self._seed_availability(doctors)
        patients = self._seed_patients()
        self._seed_symptoms_and_conditions()
        self._seed_appointments(patients, doctors, departments)
        self._seed_ambulance_requests(patients)
        self._seed_feedback(patients, doctors)

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write("Admin login: admin / CarePulse@123")
        self.stdout.write("Doctor login: dr.ananya.sharma / CarePulse@123")
        self.stdout.write("Patient login: patient.rahul / CarePulse@123")

    # -- helpers ---------------------------------------------------------
    def _flush(self):
        Appointment.objects.all().delete()
        AmbulanceRequest.objects.all().delete()
        Feedback.objects.all().delete()
        Doctor.objects.all().delete()
        Department.objects.all().delete()
        Condition.objects.all().delete()
        Symptom.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def _seed_departments(self):
        departments = {}
        for name, icon, description in DEPARTMENTS:
            department, _ = Department.objects.update_or_create(
                name=name,
                defaults={
                    "slug": slugify(name),
                    "icon": icon,
                    "description": description,
                    "is_active": True,
                },
            )
            departments[name] = department
        return departments

    def _seed_doctors(self, departments):
        doctors = []
        password = make_password("CarePulse@123")
        for full_name, dept_name, designation, qualifications, experience in DOCTORS:
            username = "dr." + slugify(full_name).replace("-", ".")
            user, _ = User.objects.update_or_create(
                username=username,
                defaults={
                    "first_name": full_name.split()[0],
                    "last_name": " ".join(full_name.split()[1:]),
                    "email": f"{username}@carepulse.local",
                    "role": Role.DOCTOR,
                    "password": password,
                    "is_verified": True,
                },
            )
            doctor, _ = Doctor.objects.update_or_create(
                slug=slugify(full_name),
                defaults={
                    "user": user,
                    "full_name": full_name,
                    "department": departments[dept_name],
                    "designation": designation,
                    "qualifications": qualifications,
                    "experience_years": experience,
                    "languages_spoken": "English, Hindi",
                    "consultation_fee": random.choice([500, 700, 900, 1200]),
                    "bio": f"Dr. {full_name} is a {designation.lower()} with {experience} years "
                    f"of experience in {dept_name.lower()}.",
                    "is_active": True,
                    "accepts_walk_ins": random.choice([True, False]),
                },
            )
            doctors.append(doctor)
        return doctors

    def _seed_availability(self, doctors):
        for doctor in doctors:
            DoctorAvailability.objects.filter(doctor=doctor).delete()
            weekdays = random.sample(range(0, 6), k=3)
            for weekday in weekdays:
                DoctorAvailability.objects.create(
                    doctor=doctor,
                    weekday=weekday,
                    start_time=dt.time(9, 0),
                    end_time=dt.time(13, 0),
                    slot_minutes=20,
                )

    def _seed_patients(self):
        patients = []
        password = make_password("CarePulse@123")
        names = [
            ("Rahul", "Verma"), ("Priyanka", "Joshi"), ("Aditya", "Kulkarni"),
            ("Sanya", "Malhotra"), ("Karan", "Mehta"),
        ]
        for first, last in names:
            username = f"patient.{first.lower()}"
            user, _ = User.objects.update_or_create(
                username=username,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "email": f"{username}@example.com",
                    "role": Role.PATIENT,
                    "password": password,
                    "phone_number": f"+9198{random.randint(10000000, 99999999)}",
                    "is_verified": True,
                },
            )
            patients.append(user)

        User.objects.update_or_create(
            username="admin.staff",
            defaults={
                "first_name": "Front",
                "last_name": "Desk",
                "email": "frontdesk@carepulse.local",
                "role": Role.STAFF,
                "password": password,
                "is_staff": True,
                "is_verified": True,
            },
        )
        return patients

    def _seed_symptoms_and_conditions(self):
        symptom_objs = {}
        for name in SYMPTOMS:
            symptom, _ = Symptom.objects.update_or_create(
                name=name,
                defaults={"description": name.replace("_", " ").capitalize()},
            )
            symptom_objs[name] = symptom

        for name, symptom_names, severity, dept_name in CONDITIONS:
            department = Department.objects.filter(name=dept_name).first()
            condition, _ = Condition.objects.update_or_create(
                name=name,
                defaults={
                    "severity": severity,
                    "recommended_department": department,
                    "description": f"Commonly presents with {', '.join(symptom_names).replace('_', ' ')}.",
                    "self_care_advice": "Rest, stay hydrated, and monitor symptoms.",
                },
            )
            condition.symptoms.set([symptom_objs[s] for s in symptom_names])

    def _seed_appointments(self, patients, doctors, departments):
        today = dt.date.today()
        statuses = list(Appointment.Status)
        for _ in range(25):
            patient = random.choice(patients)
            doctor = random.choice(doctors)
            offset = random.randint(-10, 10)
            date = today + dt.timedelta(days=offset)
            hour = random.choice(range(9, 13))
            minute = random.choice([0, 20, 40])
            status = random.choice(statuses) if offset < 0 else random.choice(
                [Appointment.Status.PENDING, Appointment.Status.CONFIRMED]
            )
            Appointment.objects.get_or_create(
                doctor=doctor,
                scheduled_date=date,
                scheduled_time=dt.time(hour, minute),
                defaults={
                    "patient": patient,
                    "department": doctor.department,
                    "reason": random.choice(
                        ["Routine checkup", "Follow-up", "New symptoms", "Consultation"]
                    ),
                    "status": status,
                },
            )

    def _seed_ambulance_requests(self, patients):
        priorities = list(AmbulanceRequest.Priority)
        statuses = list(AmbulanceRequest.Status)
        for i in range(6):
            AmbulanceRequest.objects.get_or_create(
                contact_name=f"{patients[i % len(patients)].get_full_name()}",
                contact_phone=f"+9199{random.randint(10000000, 99999999)}",
                defaults={
                    "requester": patients[i % len(patients)],
                    "pickup_address": "123 MG Road, Nagpur, Maharashtra",
                    "patient_condition": random.choice(
                        ["Fever and weakness", "Fall injury", "Chest discomfort"]
                    ),
                    "priority": random.choice(priorities),
                    "status": random.choice(statuses),
                },
            )

    def _seed_feedback(self, patients, doctors):
        for _ in range(15):
            Feedback.objects.create(
                author=random.choice(patients),
                doctor=random.choice(doctors),
                category=random.choice(list(Feedback.Category)),
                rating=random.randint(3, 5),
                message=random.choice(
                    [
                        "Great experience, the staff was very helpful.",
                        "Doctor explained everything clearly.",
                        "Wait time could be shorter, but care was excellent.",
                        "Very professional and courteous team.",
                    ]
                ),
                is_published=True,
            )
