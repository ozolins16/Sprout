from django.contrib import admin

from .models import Business, Service


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'owner', 'created_at')
    list_filter = ('category',)
    search_fields = ('name', 'owner__username')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'business', 'price', 'duration_minutes')
    list_filter = ('business',)
    search_fields = ('name',)
