# CarePulse

> ## Educational Portfolio Project
>
> CarePulse is a healthcare management web application developed by **Chitralekha Ghadge** as an academic and portfolio project to demonstrate full-stack Django development skills.
>
> This project is intended for **learning, research, and portfolio purposes only**. It is **not designed for production use in hospitals or healthcare organizations**, and it should not be used for real medical decision-making or patient care.
>
> The project showcases concepts such as role-based authentication, appointment management, doctor scheduling, symptom assessment, dashboard analytics, and responsive UI development while following Django best practices.
A modern healthcare management platform built using Django 5 to demonstrate scalable web application architecture, clean code organization, and full-stack development practices.
---

## Project Purpose

The primary goal of this project is to demonstrate practical software engineering concepts learned during academic study.

The project focuses on:

- Django full-stack development
- Role-based authentication and authorization
- Database design and normalization
- Appointment scheduling
- Healthcare workflow management
- Responsive frontend development
- Dashboard analytics
- Clean project architecture
- Deployment-ready project structure
- Software development best practices

This project was developed independently for educational and portfolio purposes to showcase technical skills during internships, placements, and software engineering interviews.
## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Database Schema](#database-schema)
- [Technologies Used](#technologies-used)
- [Folder Structure](#folder-structure)
- [Installation](#installation)
- [Demo Accounts](#demo-accounts)
- [Screenshots](#screenshots)
- [Deployment](#deployment)
- [Future Scope](#future-scope)
- [License](#license)

---

## Features

### Patient experience
- Self-service registration and profile management
- Live appointment booking — doctor/department filters, real open time slots
  (computed from a doctor's recurring weekly availability minus existing
  bookings), AJAX slot refresh, and a hard database constraint preventing
  double-booking
- Explainable symptom checker: select symptoms, get a transparent,
  percentage-scored condition match with recommended department — no
  black-box model, fully auditable via the admin panel
- Ambulance request form (works even for anonymous/emergency use)
- Feedback and rating submission
- Personal dashboard: upcoming appointments, triage history, quick actions

### Doctor experience
- Dedicated dashboard: today's schedule, upcoming appointment count,
  completed visits, unique patients seen

### Staff / Admin experience
- Operations dashboard with analytics cards and Chart.js visualizations
  (7-day appointment trend, status breakdown, bookings by department)
- Doctor & department management (create/update/delete, weekly availability
  slots)
- Ambulance request queue with priority/status filtering
- Feedback moderation with aggregate rating stats
- Full Django admin with search, filters, inlines, and autocomplete

### Platform-wide
- Role-based authentication & authorization (Patient / Doctor / Staff / Admin)
- Light/dark theme toggle (persisted via `localStorage` and synced to the
  user's account)
- Responsive sidebar app shell + public marketing site sharing one design
  system
- Search, filtering, and pagination on every list view
- Django messages framework for user feedback
- Custom 400/403/404/500 error pages
- Structured logging to console + rotating file handler
- Environment-driven settings (SQLite for dev, any `DATABASE_URL` — e.g.
  Postgres — for production)

---

## Architecture

CarePulse is split into eight single-responsibility Django apps under `apps/`:

| App | Responsibility |
|---|---|
| `accounts` | Custom `User` model, roles, registration, profile, settings |
| `core` | Landing/about/contact pages, shared middleware, context processors, error handlers |
| `doctors` | Departments, doctor directory, weekly availability |
| `appointments` | Booking, slot computation, appointment lifecycle |
| `triage` | Symptom checker (transparent scoring, not a black-box model) |
| `ambulance` | Emergency transport requests & dispatch tracking |
| `feedback` | Patient satisfaction ratings & testimonials |
| `dashboard` | Role-aware analytics dashboard, notifications, demo data seeding |

Each app owns its own `models.py`, `forms.py`, `views.py` (class-based views
throughout, with a few functional views where that was the simpler tool),
`urls.py` (namespaced), and `admin.py`. Cross-cutting concerns — access
control mixins, logging middleware, template context — live in `apps/core`
so every app can reuse them instead of duplicating logic.

Templates follow the same pattern: a single `templates/base.html` (public
navbar/footer) and `templates/dashboard/_dashboard_base.html` (sidebar app
shell) that every page extends, plus a shared `includes/_form.html` partial
so every form in the project renders identically without repeating Bootstrap
markup.

---

## Database Schema

Highlights of the relational design (see each app's `models.py` for full
field lists, indexes, and constraints):

- **`accounts.User`** — extends `AbstractUser` with a `role` choice field
  (Patient/Doctor/Staff/Admin), phone/DOB/avatar, and theme preference.
- **`doctors.Department` → `doctors.Doctor` → `doctors.DoctorAvailability`** —
  a doctor's bookable hours are normalized into a weekly-recurrence table
  instead of a free-text field, so real slots can be computed.
- **`appointments.Appointment`** — foreign keys to patient, doctor, and
  department; a **partial unique constraint** on
  `(doctor, scheduled_date, scheduled_time)` (excluding cancelled rows) makes
  double-booking impossible at the database level, not just in application
  code.
- **`triage.Symptom` ⇄ `triage.Condition`** — a many-to-many relationship
  between symptoms and conditions that staff can edit in the admin panel;
  `triage.TriageAssessment` records each patient's session for audit/history.
- **`ambulance.AmbulanceRequest`** — priority/status choice fields for
  dispatch triage.
- **`feedback.Feedback`** — validated 1–5 rating, category choices, optional
  doctor link.
- **`dashboard.Notification`** — lightweight per-user notification feed.

All models use `Meta.indexes`/`constraints` where they matter for query
performance or data integrity, and `choices` + validators for every
enumerable or bounded field.

---

## Technologies Used

- **Backend:** Django 5.1 (Python 3.12)
- **Database:** SQLite (development) / any `DATABASE_URL` — Postgres
  recommended (production), via `django-environ`
- **Frontend:** Bootstrap 5.3, Bootstrap Icons, vanilla JavaScript, Chart.js
- **Static/media:** WhiteNoise (compressed, hashed static files), Pillow
- **Production server:** Gunicorn
- **Fonts:** Plus Jakarta Sans (Google Fonts)

---

## Folder Structure

```
carepulse/
├── apps/
│   ├── accounts/          # Custom user model, auth, profile, settings
│   ├── ambulance/         # Ambulance request + dispatch
│   ├── appointments/      # Booking, slot computation, lifecycle
│   ├── core/              # Landing pages, mixins, middleware, error handlers
│   ├── dashboard/         # Analytics dashboard, notifications, demo seeding
│   ├── doctors/           # Departments, doctor directory, availability
│   ├── feedback/          # Ratings & testimonials
│   └── triage/            # Symptom checker
├── carepulse/
│   ├── settings/
│   │   ├── base.py        # Shared settings
│   │   ├── development.py # Local dev overrides
│   │   └── production.py  # Security-hardened production overrides
│   ├── urls.py             # Root URL conf + custom error handlers
│   ├── wsgi.py / asgi.py
├── templates/
│   ├── base.html                       # Public site shell
│   ├── dashboard/_dashboard_base.html  # Sidebar app shell
│   ├── includes/                       # Reusable partials (forms, pagination)
│   ├── errors/                         # 400/403/404/500
│   └── <app>/...                       # Per-app templates
├── static/
│   ├── css/theme.css        # Design tokens (light/dark CSS variables)
│   ├── css/components.css   # Component library (cards, sidebar, buttons…)
│   └── js/                  # Theme toggle, AJAX slot loading, UI helpers
├── requirements.txt
├── .env.example
├── gunicorn.conf.py
├── Procfile
├── build.sh                # Render build script
├── render.yaml             # Render blueprint
├── DEPLOYMENT.md
└── manage.py
```

---

## Installation

### Prerequisites
- Python 3.12+
- pip / venv

### Steps

```bash
# 1. Clone and enter the project
git clone https://github.com/<your-username>/carepulse.git
cd carepulse

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# edit .env if needed — defaults work out of the box for local development

# 5. Apply migrations
python manage.py migrate

# 6. (Optional but recommended) Seed realistic demo data
python manage.py seed_demo_data

# 7. Create your own superuser (skip if you only need the seeded admin)
python manage.py createsuperuser

# 8. Run the development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`.

---

## Demo Accounts

After running `python manage.py seed_demo_data`, these accounts are available
(all with password `CarePulse@123`):

| Role | Username |
|---|---|
| Doctor | `dr.ananya.sharma` (or any other `dr.<first>.<last>`) |
| Patient | `patient.rahul` |
| Front-desk staff | `admin.staff` |

Create a superuser separately with `python manage.py createsuperuser` for
full Django admin + Administrator-role dashboard access.

---

## Screenshots

> _Add screenshots here once you've run the app locally — suggested shots:_
- `docs/screenshots/landing.png` — public landing page
- `docs/screenshots/admin-dashboard.png` — staff analytics dashboard
- `docs/screenshots/booking.png` — appointment booking with live slots
- `docs/screenshots/triage.png` — symptom checker result
- `docs/screenshots/dark-mode.png` — dark theme

---

## Deployment

See [`DEPLOYMENT.md`](DEPLOYMENT.md) for full, platform-specific instructions
covering **Render**, **Railway**, and **PythonAnywhere**, including
environment variables, static/media file handling, and database setup.

Quick reference:
```bash
DJANGO_SETTINGS_MODULE=carepulse.settings.production python manage.py collectstatic --no-input
DJANGO_SETTINGS_MODULE=carepulse.settings.production python manage.py migrate
gunicorn -c gunicorn.conf.py carepulse.wsgi:application
```

---

## Future Scope

- REST API (Django REST Framework) to power a companion mobile app
- Async notifications (email/SMS) on appointment confirmation, reminders,
  and ambulance dispatch updates via Celery + Redis
- Semantic-embedding based "similar case" search for the triage tool
- Doctor-side prescription and visit-notes module
- Payment integration for consultation fees
- Multi-language UI (the original requirements were multilingual; CarePulse's
  `i18n`-ready settings make this a natural next step via Django's
  translation framework)
- WebSocket-based live queue/wait-time updates for the front desk

---

## License

Copyright © 2026 Chitralekha Ghadge

This project was developed as a personal academic and portfolio project.

The source code is shared for educational demonstration purposes only.

You may view this repository to understand the implementation and architecture.

Copying, redistributing, publishing, selling, or using substantial portions of this source code without explicit permission from the author is not permitted.

If you wish to reference this project, please provide appropriate credit to the author.

# Disclaimer

This application is a student portfolio project created solely for educational and demonstration purposes.

The symptom checker included in this application is a rule-based educational implementation and **does not provide medical advice, diagnosis, or treatment**.

The project should not be used in real healthcare environments or for making actual medical decisions.

All data used in the application is either fictional or demonstration data created for testing purposes.

# Author

**Chitralekha Ghadge**

MCA (Artificial Intelligence & Machine Learning)

Portfolio Project • Django Developer • Python Developer

GitHub: https://github.com/chitralekha-ghadge
