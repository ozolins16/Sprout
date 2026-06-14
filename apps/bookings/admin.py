from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client', 'staff', 'service', 'start_datetime', 'status')
    list_filter = ('status', 'staff__business')
    search_fields = ('client__username', 'staff__user__username')
    date_hierarchy = 'start_datetime'
