from django.urls import path

from . import views

app_name = 'bookings'

urlpatterns = [
    path('book/<int:business_id>/', views.book_service_pick, name='book_service'),
    path(
        'book/<int:business_id>/service/<int:service_id>/',
        views.book_staff_pick,
        name='book_staff',
    ),
    path(
        'book/<int:business_id>/service/<int:service_id>/staff/<int:staff_id>/',
        views.book_datetime_pick,
        name='book_datetime',
    ),
    path(
        'book/<int:business_id>/service/<int:service_id>/staff/<int:staff_id>/confirm/',
        views.book_confirm,
        name='book_confirm',
    ),
    path('book/success/<int:appointment_id>/', views.book_success, name='book_success'),
    path('api/slots/', views.slots_api, name='slots_api'),
    path('my/bookings/', views.client_bookings, name='client_bookings'),
    path('my/bookings/<int:pk>/cancel/', views.client_booking_cancel, name='client_booking_cancel'),
]
