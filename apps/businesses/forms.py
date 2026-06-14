from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

from .models import DAY_CHOICES, Business, Service, Staff

User = get_user_model()


class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ('name', 'category')
        labels = {
            'name': _('Business name'),
            'category': _('Category'),
        }


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ('name', 'price', 'duration_minutes')
        labels = {
            'name': _('Service name'),
            'price': _('Price'),
            'duration_minutes': _('Duration (minutes)'),
        }

    def clean_duration_minutes(self):
        duration = self.cleaned_data['duration_minutes']
        if duration <= 0:
            raise forms.ValidationError(_('Duration must be a positive number of minutes.'))
        return duration

    def clean_price(self):
        price = self.cleaned_data['price']
        if price < 0:
            raise forms.ValidationError(_('Price cannot be negative.'))
        return price


class StaffCreationForm(forms.Form):
    username = forms.CharField(label=_('Username'), max_length=150)
    email = forms.EmailField(label=_('Email'))
    first_name = forms.CharField(label=_('First name'), max_length=150, required=False)
    last_name = forms.CharField(label=_('Last name'), max_length=150, required=False)
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(_('A user with that username already exists.'))
        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        validate_password(password)
        return password

    def save(self, *, business: Business) -> Staff:
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data.get('first_name', ''),
            last_name=self.cleaned_data.get('last_name', ''),
        )
        user.role = User.Role.STAFF
        user.save(update_fields=['role'])
        return Staff.objects.create(user=user, business=business)


class StaffScheduleForm(forms.ModelForm):
    working_days = forms.MultipleChoiceField(
        choices=DAY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label=_('Working days'),
        required=False,
    )

    class Meta:
        model = Staff
        fields = ('working_days', 'start_time', 'end_time', 'bio', 'photo')
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial['working_days'] = [str(n) for n in self.instance.working_day_numbers()]

    def clean_working_days(self):
        days = self.cleaned_data.get('working_days', [])
        days_sorted = sorted(int(d) for d in days)
        return ','.join(str(d) for d in days_sorted)

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_time')
        end = cleaned.get('end_time')
        if start and end and start >= end:
            raise forms.ValidationError(_('End time must be later than start time.'))
        return cleaned
