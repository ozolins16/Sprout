from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import ClientRegistrationForm, OwnerRegistrationForm


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
    extra_context = {'heading': 'Create a client account', 'role_label': 'client'}


class OwnerRegisterView(_RegisterView):
    form_class = OwnerRegistrationForm
    success_url = reverse_lazy('businesses:business_create')
    extra_context = {'heading': 'Register your business', 'role_label': 'owner'}


def home(request):
    return render(request, 'home.html')
