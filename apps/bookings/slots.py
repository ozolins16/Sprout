"""Available-slot calculation for the booking flow.

Given a staff member, service, and date, produces the list of 15-minute
interval start times where a new appointment of that service's duration
would fit inside the staff member's working window without overlapping
an existing confirmed booking.
"""
from __future__ import annotations

from datetime import date as date_cls
from datetime import datetime, timedelta

from django.utils import timezone

from apps.businesses.models import Service, Staff

from .models import Appointment

SLOT_STEP = timedelta(minutes=15)


def get_available_slots(
    staff: Staff,
    service: Service,
    target_date: date_cls,
) -> list[str]:
    if target_date.weekday() not in staff.working_day_numbers():
        return []

    tz = timezone.get_current_timezone()
    day_start = timezone.make_aware(
        datetime.combine(target_date, staff.start_time), tz,
    )
    day_end = timezone.make_aware(
        datetime.combine(target_date, staff.end_time), tz,
    )
    service_duration = timedelta(minutes=service.duration_minutes)
    now = timezone.now()

    existing = (
        Appointment.objects
        .filter(
            staff=staff,
            status=Appointment.Status.CONFIRMED,
            start_datetime__gte=day_start,
            start_datetime__lt=day_end,
        )
        .select_related('service')
    )
    busy = [
        (a.start_datetime, a.start_datetime + timedelta(minutes=a.service.duration_minutes))
        for a in existing
    ]

    slots: list[str] = []
    cursor = day_start
    while cursor + service_duration <= day_end:
        slot_end = cursor + service_duration
        if cursor >= now and not any(
            slot_end > b_start and cursor < b_end for b_start, b_end in busy
        ):
            slots.append(cursor.astimezone(tz).strftime('%H:%M'))
        cursor += SLOT_STEP
    return slots


def is_slot_available(staff: Staff, service: Service, start_dt) -> bool:
    """Re-check at confirmation time that the chosen slot is still free."""
    target_date = start_dt.astimezone(timezone.get_current_timezone()).date()
    time_str = start_dt.astimezone(timezone.get_current_timezone()).strftime('%H:%M')
    return time_str in get_available_slots(staff, service, target_date)
