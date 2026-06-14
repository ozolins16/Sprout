"""Booking-related transactional emails sent via Resend.

If Resend is not configured or the request fails, we log and swallow the error:
a missing notification must never block a successful booking.
"""
from __future__ import annotations

import logging

from django.conf import settings
from django.template.loader import render_to_string

from .models import Appointment

logger = logging.getLogger(__name__)


def send_booking_confirmation(appointment: Appointment) -> None:
    api_key = getattr(settings, 'RESEND_API_KEY', '')
    to_email = appointment.client.email
    if not api_key or not to_email:
        logger.info(
            'Skipping booking email (api_key=%s, recipient=%s)',
            bool(api_key), bool(to_email),
        )
        return

    subject = f'Booking confirmed — {appointment.service.name} at {appointment.staff.business.name}'
    context = {'appointment': appointment}
    text_body = render_to_string('bookings/email/booking_confirmation.txt', context)
    html_body = render_to_string('bookings/email/booking_confirmation.html', context)

    try:
        import resend  # imported lazily so missing pkg won't crash the app
        resend.api_key = api_key
        resend.Emails.send({
            'from': settings.DEFAULT_FROM_EMAIL,
            'to': [to_email],
            'subject': subject,
            'text': text_body,
            'html': html_body,
        })
    except Exception:  # noqa: BLE001 — third-party SDK exposes many error types
        logger.exception('Failed to send booking confirmation email')
