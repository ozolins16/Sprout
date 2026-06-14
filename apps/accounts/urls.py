from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.ClientRegisterView.as_view(), name='register'),
    path('register/owner/', views.OwnerRegisterView.as_view(), name='register_owner'),
    path('login/', views.RoleAwareLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
