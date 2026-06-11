from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Business, Service


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
