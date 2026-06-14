from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Appointment(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = 'confirmed', _('Confirmed')
        CANCELLED = 'cancelled', _('Cancelled')

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments',
    )
    staff = models.ForeignKey(
        'businesses.Staff',
        on_delete=models.CASCADE,
        related_name='appointments',
    )
    service = models.ForeignKey(
        'businesses.Service',
        on_delete=models.CASCADE,
        related_name='appointments',
    )
    start_datetime = models.DateTimeField(_('start'))
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-start_datetime',)
        verbose_name = _('appointment')
        verbose_name_plural = _('appointments')

    def __str__(self) -> str:
        return f'{self.service.name} with {self.staff} at {self.start_datetime:%Y-%m-%d %H:%M}'

    @property
    def end_datetime(self):
        return self.start_datetime + timedelta(minutes=self.service.duration_minutes)
