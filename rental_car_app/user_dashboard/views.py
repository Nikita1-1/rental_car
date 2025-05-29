from django.conf import settings
from django.shortcuts import get_object_or_404, render
from user_auths.models import Profile, User
from django.shortcuts import render, redirect
from django.db import models
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from car.models import *
from user_auths.models import Profile, User
from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required, user_passes_test
import os
from user_auths.forms import ProfileUpdateForm, UserUpdateForm
# Create your views here.


@login_required
def dashboard(request):
    profile = request.user.profile
    bookings = Booking.objects.filter(profile=profile, payment_status__in=["paid", 'unpaid'])
    total_spent = Booking.objects.filter(profile=profile, payment_status="paid").aggregate(amount=models.Sum('total_price'))

    context = {
        'bookings': bookings,
        'total_spent': total_spent['amount'] if total_spent['amount'] else 0,
    }
    return render(request, 'user_dashboard/dashboard.html', context)


@login_required
def booking_detail(request, booking_id):
    booking = Booking.objects.get(booking_id=booking_id)
    context = {
        'booking': booking,

    }
    return render(request, 'user_dashboard/booking_detail.html', context)


@login_required
def bookings(request):
    bookings = Booking.objects.filter(profile__user=request.user, payment_status="paid")

    context = {
        "bookings":bookings,
    }
    return render(request, "user_dashboard/bookings.html", context)


@login_required
def profile(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect("dashboard:profile")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        "profile":profile,
        "u_form":u_form,
        "p_form":p_form,
    }
    return render(request, "user_dashboard/profile.html", context)


@login_required
def password_changed(request):
    messages.success(request, "Password Changed Successfully")
    return render(request, "user_dashboard/password_changed.html")

@login_required
def cancel_booking(request, booking_id):
    if request.method != "POST":
        return redirect("dashboard:bookings")
    
    booking = get_object_or_404(
        Booking,
        booking_id=booking_id,
        profile__user=request.user
    )

    booking_in_session = request.session.get('booking', [])
    if booking_id in booking_in_session:
        booking_in_session.remove(booking_id)
        request.session['booking'] = booking_in_session
        request.session.modified = True
    
    booking.delete()

    messages.success(request, "Booking Cancelled Successfully")
    return redirect("dashboard:bookings")

@login_required
def dashboard_profile_update(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard:profile')
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'user_dashboard/profile.html', {'form':form})