from django.urls import path

from . import views

app_name = 'businesses'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('business/new/', views.business_create, name='business_create'),
    path('services/', views.service_list, name='service_list'),
    path('services/new/', views.service_create, name='service_create'),
    path('services/<int:pk>/edit/', views.service_update, name='service_update'),
    path('services/<int:pk>/delete/', views.service_delete, name='service_delete'),
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/new/', views.staff_create, name='staff_create'),
    path('staff/<int:pk>/delete/', views.staff_delete, name='staff_delete'),
]
