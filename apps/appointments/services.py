"""Business logic for computing bookable appointment slots.

Kept separate from views/models so it is independently unit-testable and
reusable from both the booking form (AJAX endpoint) and any future API.
"""

from __future__ import annotations

import datetime as dt

from apps.doctors.models import Doctor

from .models import Appointment


def _iter_slots(start: dt.time, end: dt.time, minutes: int):
    current = dt.datetime.combine(dt.date.today(), start)
    end_dt = dt.datetime.combine(dt.date.today(), end)
    step = dt.timedelta(minutes=minutes)
    while current + step <= end_dt:
        yield current.time()
        current += step


def get_available_slots(doctor: Doctor, target_date: dt.date) -> list[dt.time]:
    """Return open appointment start-times for ``doctor`` on ``target_date``.

    Combines the doctor's recurring weekly availability with already-booked
    (non-cancelled) appointments on that date to compute the free slots.
    """
    weekday = target_date.weekday()
    availability_slots = doctor.availability_slots.filter(weekday=weekday)

    booked_times = set(
        Appointment.objects.filter(
            doctor=doctor,
            scheduled_date=target_date,
        )
        .exclude(status=Appointment.Status.CANCELLED)
        .values_list("scheduled_time", flat=True)
    )

    today = dt.date.today()
    now_time = dt.datetime.now().time()

    open_slots: list[dt.time] = []
    for window in availability_slots:
        for slot_time in _iter_slots(window.start_time, window.end_time, window.slot_minutes):
            if slot_time in booked_times:
                continue
            if target_date == today and slot_time <= now_time:
                continue
            open_slots.append(slot_time)

    return sorted(set(open_slots))
