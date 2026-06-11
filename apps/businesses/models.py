from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


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
