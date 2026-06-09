from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        CLIENT = 'client', _('Client')
        STAFF = 'staff', _('Staff')
        OWNER = 'owner', _('Owner')

    role = models.CharField(
        _('role'),
        max_length=10,
        choices=Role.choices,
        default=Role.CLIENT,
    )

    @property
    def is_owner(self) -> bool:
        return self.role == self.Role.OWNER

    @property
    def is_staff_member(self) -> bool:
        return self.role == self.Role.STAFF

    @property
    def is_client(self) -> bool:
        return self.role == self.Role.CLIENT
