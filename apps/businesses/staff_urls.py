from django.urls import path

from apps.bookings.views import staff_appointments

from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.staff_dashboard, name='dashboard'),
    path('schedule/', views.staff_schedule, name='schedule'),
    path('appointments/', staff_appointments, name='appointments'),
]
