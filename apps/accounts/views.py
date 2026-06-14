from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView

from .forms import ClientRegistrationForm, OwnerRegistrationForm


class RoleAwareLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self) -> str:
        redirect_to = self.get_redirect_url()
        if redirect_to:
            return redirect_to
        user = self.request.user
        if user.is_owner:
            return reverse('businesses:dashboard')
        if user.is_staff_member:
            return reverse('staff:dashboard')
        return reverse('home')


class _RegisterView(CreateView):
    template_name = 'accounts/register.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


class ClientRegisterView(_RegisterView):
    form_class = ClientRegistrationForm
    success_url = reverse_lazy('home')
    extra_context = {'heading': _('Create a client account'), 'role_label': 'client'}


class OwnerRegisterView(_RegisterView):
    form_class = OwnerRegistrationForm
    success_url = reverse_lazy('businesses:business_create')
    extra_context = {'heading': _('Register your business'), 'role_label': 'owner'}


def home(request):
    # Import inside the view to avoid an app-loading import cycle between
    # accounts and businesses at module import time.
    from apps.businesses.models import Business

    businesses = Business.objects.all().order_by('name')
    return render(request, 'home.html', {'businesses': businesses})
