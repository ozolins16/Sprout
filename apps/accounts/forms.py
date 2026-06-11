from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import User


class _BaseRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        labels = {
            'username': _('Username'),
            'email': _('Email'),
            'first_name': _('First name'),
            'last_name': _('Last name'),
        }


class ClientRegistrationForm(_BaseRegistrationForm):
    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        user.role = User.Role.CLIENT
        if commit:
            user.save()
        return user


class OwnerRegistrationForm(_BaseRegistrationForm):
    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        user.role = User.Role.OWNER
        if commit:
            user.save()
        return user
