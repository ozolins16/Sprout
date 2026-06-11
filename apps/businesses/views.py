from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from apps.accounts.decorators import owner_required

from .forms import BusinessForm, ServiceForm
from .models import Business, Service, seed_default_services


def _get_owner_business(user) -> Business | None:
    return Business.objects.filter(owner=user).first()


@owner_required
def dashboard(request):
    business = _get_owner_business(request.user)
    if business is None:
        return redirect('businesses:business_create')
    return render(request, 'businesses/dashboard.html', {'business': business})


@owner_required
def business_create(request):
    if _get_owner_business(request.user) is not None:
        return redirect('businesses:dashboard')

    if request.method == 'POST':
        form = BusinessForm(request.POST)
        if form.is_valid():
            business = form.save(commit=False)
            business.owner = request.user
            business.save()
            seed_default_services(business)
            messages.success(request, _('Business created. Default services were added.'))
            return redirect('businesses:dashboard')
    else:
        form = BusinessForm()

    return render(request, 'businesses/business_form.html', {'form': form})


@owner_required
def service_list(request):
    business = _get_owner_business(request.user)
    if business is None:
        return redirect('businesses:business_create')
    services = business.services.all()
    return render(
        request,
        'businesses/service_list.html',
        {'business': business, 'services': services},
    )


@owner_required
def service_create(request):
    business = _get_owner_business(request.user)
    if business is None:
        return redirect('businesses:business_create')

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.business = business
            service.save()
            messages.success(request, _('Service created.'))
            return redirect('businesses:service_list')
    else:
        form = ServiceForm()

    return render(
        request,
        'businesses/service_form.html',
        {'form': form, 'mode': 'create'},
    )


@owner_required
def service_update(request, pk: int):
    business = _get_owner_business(request.user)
    service = get_object_or_404(Service, pk=pk, business=business)

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, _('Service updated.'))
            return redirect('businesses:service_list')
    else:
        form = ServiceForm(instance=service)

    return render(
        request,
        'businesses/service_form.html',
        {'form': form, 'service': service, 'mode': 'edit'},
    )


@owner_required
@require_http_methods(['GET', 'POST'])
def service_delete(request, pk: int):
    business = _get_owner_business(request.user)
    service = get_object_or_404(Service, pk=pk, business=business)

    if request.method == 'POST':
        service.delete()
        messages.success(request, _('Service deleted.'))
        return redirect('businesses:service_list')

    return render(
        request,
        'businesses/service_confirm_delete.html',
        {'service': service},
    )
