from django.contrib import admin

from .models import Business, Service, Staff


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'owner', 'created_at')
    list_filter = ('category',)
    search_fields = ('name', 'owner__username')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'business', 'price', 'duration_minutes')
    list_filter = ('business',)
    search_fields = ('name',)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'business', 'start_time', 'end_time', 'working_days')
    list_filter = ('business',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
