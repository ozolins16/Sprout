from datetime import datetime, date as date_cls, timedelta
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_http_methods

from apps.businesses.models import Business, Service, Staff

from .emails import send_booking_confirmation
from .models import Appointment
from .slots import get_available_slots, is_slot_available


# Step 1: pick a service
def book_service_pick(request, business_id: int):
    business = get_object_or_404(Business, pk=business_id)
    services = business.services.all()
    return render(
        request,
        'bookings/book_service.html',
        {'business': business, 'services': services},
    )


# Step 2: pick a staff member
def book_staff_pick(request, business_id: int, service_id: int):
    business = get_object_or_404(Business, pk=business_id)
    service = get_object_or_404(Service, pk=service_id, business=business)
    staff_members = business.staff.select_related('user').all()
    return render(
        request,
        'bookings/book_staff.html',
        {'business': business, 'service': service, 'staff_members': staff_members},
    )


# Step 3: pick date + time (AJAX)
def book_datetime_pick(request, business_id: int, service_id: int, staff_id: int):
    business = get_object_or_404(Business, pk=business_id)
    service = get_object_or_404(Service, pk=service_id, business=business)
    staff = get_object_or_404(Staff, pk=staff_id, business=business)

    today = timezone.localdate()
    max_date = today + timedelta(days=30)
    return render(
        request,
        'bookings/book_datetime.html',
        {
            'business': business,
            'service': service,
            'staff': staff,
            'today': today.isoformat(),
            'max_date': max_date.isoformat(),
            'api_url': reverse('bookings:slots_api') + f'?staff={staff.id}&service={service.id}',
            'confirm_url': reverse(
                'bookings:book_confirm',
                args=[business.id, service.id, staff.id],
            ),
        },
    )


@require_GET
def slots_api(request):
    try:
        staff_id = int(request.GET['staff'])
        service_id = int(request.GET['service'])
        date_str = request.GET['date']
        target_date = date_cls.fromisoformat(date_str)
    except (KeyError, ValueError):
        return HttpResponseBadRequest('Invalid parameters')

    staff = get_object_or_404(Staff, pk=staff_id)
    service = get_object_or_404(Service, pk=service_id)
    if service.business_id != staff.business_id:
        return HttpResponseBadRequest('Service does not belong to that staff member.')

    slots = get_available_slots(staff, service, target_date)
    return JsonResponse({'slots': slots})


@require_http_methods(['GET', 'POST'])
def book_confirm(request, business_id: int, service_id: int, staff_id: int):
    business = get_object_or_404(Business, pk=business_id)
    service = get_object_or_404(Service, pk=service_id, business=business)
    staff = get_object_or_404(Staff, pk=staff_id, business=business)

    date_str = request.GET.get('date') or request.POST.get('date')
    time_str = request.GET.get('time') or request.POST.get('time')
    if not (date_str and time_str):
        return HttpResponseBadRequest('Missing date or time.')
    try:
        naive = datetime.strptime(f'{date_str} {time_str}', '%Y-%m-%d %H:%M')
    except ValueError:
        return HttpResponseBadRequest('Invalid date or time format.')
    start_dt = timezone.make_aware(naive, timezone.get_current_timezone())

    # Gate: clients only. Anyone else -> login (with next= back to this URL).
    if not request.user.is_authenticated or not request.user.is_client:
        next_url = request.get_full_path()
        login_url = reverse('accounts:login') + '?' + urlencode({'next': next_url})
        return redirect(login_url)

    if request.method == 'POST':
        if not is_slot_available(staff, service, start_dt):
            messages.error(request, _('Sorry, that slot is no longer available.'))
            return redirect(
                'bookings:book_datetime',
                business_id=business.id,
                service_id=service.id,
                staff_id=staff.id,
            )
        appointment = Appointment.objects.create(
            client=request.user,
            staff=staff,
            service=service,
            start_datetime=start_dt,
        )
        send_booking_confirmation(appointment)
        return redirect('bookings:book_success', appointment_id=appointment.id)

    return render(
        request,
        'bookings/book_confirm.html',
        {
            'business': business,
            'service': service,
            'staff': staff,
            'start_dt': start_dt,
            'date': date_str,
            'time': time_str,
        },
    )


@login_required
def book_success(request, appointment_id: int):
    appointment = get_object_or_404(
        Appointment, pk=appointment_id, client=request.user,
    )
    return render(request, 'bookings/book_success.html', {'appointment': appointment})


@login_required
def client_bookings(request):
    if not request.user.is_client:
        return redirect('home')
    appointments = (
        Appointment.objects
        .filter(client=request.user)
        .select_related('service', 'staff__user', 'staff__business')
    )
    now = timezone.now()
    return render(
        request,
        'bookings/client_bookings.html',
        {'appointments': appointments, 'now': now},
    )


@login_required
@require_http_methods(['POST'])
def client_booking_cancel(request, pk: int):
    appointment = get_object_or_404(Appointment, pk=pk, client=request.user)
    if appointment.status != Appointment.Status.CONFIRMED:
        messages.error(request, _('This booking is already cancelled.'))
    elif appointment.start_datetime <= timezone.now():
        messages.error(request, _('Past bookings cannot be cancelled.'))
    else:
        appointment.status = Appointment.Status.CANCELLED
        appointment.save(update_fields=['status'])
        messages.success(request, _('Booking cancelled.'))
    return redirect('bookings:client_bookings')


@login_required
def staff_appointments(request):
    if not request.user.is_staff_member:
        return redirect('home')
    staff = getattr(request.user, 'staff_profile', None)
    if staff is None:
        messages.error(request, _('No staff profile is linked to your account.'))
        return redirect('staff:dashboard')

    now = timezone.now()
    upcoming = (
        Appointment.objects
        .filter(staff=staff, start_datetime__gte=now)
        .select_related('client', 'service')
        .order_by('start_datetime')
    )
    past = (
        Appointment.objects
        .filter(staff=staff, start_datetime__lt=now)
        .select_related('client', 'service')
        .order_by('-start_datetime')[:20]
    )
    return render(
        request,
        'bookings/staff_appointments.html',
        {'staff': staff, 'upcoming': upcoming, 'past': past, 'now': now},
    )
