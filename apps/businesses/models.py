from datetime import time

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


DAY_CHOICES = [
    ('0', _('Monday')),
    ('1', _('Tuesday')),
    ('2', _('Wednesday')),
    ('3', _('Thursday')),
    ('4', _('Friday')),
    ('5', _('Saturday')),
    ('6', _('Sunday')),
]
DAY_LABELS = dict(DAY_CHOICES)


class Business(models.Model):
    class Category(models.TextChoices):
        BARBERSHOP = 'barbershop', _('Barbershop')
        NAIL_SALON = 'nail_salon', _('Nail Salon')

    name = models.CharField(_('name'), max_length=120)
    category = models.CharField(
        _('category'),
        max_length=20,
        choices=Category.choices,
    )
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='business',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('business')
        verbose_name_plural = _('businesses')

    def __str__(self) -> str:
        return self.name


class Service(models.Model):
    name = models.CharField(_('name'), max_length=120)
    price = models.DecimalField(_('price'), max_digits=8, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(_('duration (minutes)'))
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='services',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('name',)
        verbose_name = _('service')
        verbose_name_plural = _('services')

    def __str__(self) -> str:
        return f'{self.name} ({self.business.name})'


DEFAULT_SERVICES: dict[str, list[tuple[str, str, int]]] = {
    Business.Category.BARBERSHOP: [
        ('Haircut', '20.00', 30),
        ('Beard Trim', '15.00', 20),
        ('Hot Towel Shave', '25.00', 40),
    ],
    Business.Category.NAIL_SALON: [
        ('Manicure', '25.00', 45),
        ('Pedicure', '30.00', 60),
        ('Gel Extensions', '45.00', 90),
    ],
}


class Staff(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_profile',
    )
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='staff',
    )
    bio = models.TextField(_('bio'), blank=True)
    photo = models.ImageField(
        _('photo'),
        upload_to='staff_photos/',
        blank=True,
        null=True,
    )
    working_days = models.CharField(
        _('working days'),
        max_length=20,
        default='0,1,2,3,4',
        help_text=_('Comma-separated day numbers: 0=Monday … 6=Sunday'),
    )
    start_time = models.TimeField(_('start time'), default=time(9, 0))
    end_time = models.TimeField(_('end time'), default=time(18, 0))

    class Meta:
        verbose_name = _('staff member')
        verbose_name_plural = _('staff')

    def __str__(self) -> str:
        return f'{self.user.get_full_name() or self.user.username} @ {self.business.name}'

    def working_day_numbers(self) -> list[int]:
        if not self.working_days:
            return []
        return [int(d) for d in self.working_days.split(',') if d.strip().isdigit()]

    def working_days_display(self) -> str:
        return ', '.join(str(DAY_LABELS[str(n)]) for n in self.working_day_numbers())


def seed_default_services(business: Business) -> None:
    """Create the default service set for a freshly created business."""
    defaults = DEFAULT_SERVICES.get(business.category, [])
    Service.objects.bulk_create([
        Service(
            business=business,
            name=name,
            price=price,
            duration_minutes=duration,
        )
        for name, price, duration in defaults
    ])
