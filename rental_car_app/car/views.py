
from email import message
import tempfile
from django.contrib import messages
from xmlrpc.client import _datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from car.models import *
from taggit.models import Tag
from django.utils import timezone
from booking.views import *
from django.http import Http404
from django.utils.html import escape
import stripe
import pprint
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.views.decorators.csrf import csrf_exempt
from datetime import date, datetime, time, timedelta
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
import re
from django.template.loader import render_to_string
from weasyprint import HTML
from django.shortcuts import redirect
from django.contrib import messages
from .models import Car, Booking, Booking_Features, Delivery, BabySeat, Racks_feature

from decimal import Decimal
import json

from django.conf import settings

# from user_auths.decorator import unauthenticated_user, allowed_users
# Create your views here.


def index(request):
    cars = Car.objects.filter(status='Available')
    context={
        'cars': cars
    }
    return render(request, 'car_main/home.html', context)


@login_required
def car_detail_page(request, slug):
    user = request.user
    profile = Profile.objects.get(user=user)

    if not request.user.is_authenticated:
        messages.warning(request, "You need to be logged in to book a car.")
        return redirect('user_auths:sign-in')

    # Get the car from the database
    try:
        car = Car.objects.get(status="Available", slug=slug)
    except Car.DoesNotExist:
        raise Http404("Car not found")

    # Default to empty values
    car_id = car_make = car_model = car_year = car_total_price = None
    checkin = checkout = check_in_time = check_out_time = None

    if request.method == "POST":
        # Get data from POST request
        car_id = request.POST.get('car_id')
        car_make = request.POST.get('car_make')
        car_model = request.POST.get('car_model')
        car_year = request.POST.get('car_year')
        car_total_price = request.POST.get('car_total_price')

        checkin = request.POST.get('checkin')
        checkout = request.POST.get('checkout')
        check_in_time = request.POST.get('time_in')
        check_out_time = request.POST.get('time_out')
    else:
        # Fallback: Get data from session
        session_data = request.session.get('selection_data_obj')
        if session_data:
            car_id = car.id  # or session_data.get('car_id') if you store it
            car_make = car.make
            car_model = car.model
            car_year = car.year
            car_total_price = session_data.get('car_total_price')

            checkin = session_data.get('checkin')
            checkout = session_data.get('checkout')
            check_in_time = session_data.get('check_in_time')
            check_out_time = session_data.get('check_out_time')

    baby_seats = BabySeat.objects.all()
    racks = Racks_feature.objects.all()
    deliveries = Delivery.objects.all()

    context = {
        'car': car,
        'racks': racks,
        'car_id': car_id,
        'car_make': car_make,
        'car_model': car_model,
        'car_year': car_year,
        'car_total_price': car_total_price,
        'checkin': checkin,
        'checkout': checkout,
        'check_in_time': check_in_time,
        'check_out_time': check_out_time,
        'deliveries': deliveries,
        'baby_seats': baby_seats,
        'user': user,
    }

    return render(request, 'car_main/car_detail.html', context)

def str_to_bool(val):
    return str(val).lower() in ['true', '1', 'yes', 'on']

def clean_price(price_str):
    return float(re.sub(r"[^\d.]", "", str(price_str)))

def parse_time_string(t_str):

    if not t_str:
        return None
    
    s = t_str.strip().lower().replace(".", "")

    m = re.match(r'^(\d{1,2}):(\d{2})\s*([ap]m)?$', s)
    if not m:
        parts = s.split(':')
        return time(int(parts[0],[1]))
    hour, minute, meridiem = m.groups()
    h = int(hour) % 12
    if meridiem == 'p':
        h += 12
    return time(h, int(minute))    

def parse_data_string(data_str):
    if not data_str:
        return None
    cleaned = data_str.replace(".", "")
    formats = [
        "%B %d, %Y",
        "%b %d, %Y",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",]
    for fmt in formats: 
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Date string '{data_str}' does not match any expected format.")

@login_required
def selected_car(request):
    profile = Profile.objects.get(user=request.user) if request.user.is_authenticated else None

    if 'selection_data_obj' in request.session:
        if request.method == "POST":
            item = request.session['selection_data_obj']

            id = int(item['car_id'])
            checkin = item['checkin']
            checkout = item['checkout']
            check_in_time = item['check_in_time']
            check_out_time = item['check_out_time']
            total_price = clean_price(item.get('total_price'))

            delivery_id = item.get('delivery', "Pick Up")  # corrected key
            baby_seat_slug = item.get('baby_seat', None)
            flight_number = item.get('flight_number', None)
            second_driver = str_to_bool(item.get('second_driver', False))
            prepaid_fuel = str_to_bool(item.get('prepaid_fuel', False))
            rack_slug = item.get('rack', None)
            delivery_address = item.get('address', None)
           

            user = request.user
            car = Car.objects.get(id=id)

            checkin_date = parse_data_string(checkin)
            checkout_date = parse_data_string(checkout)
            check_in_time = parse_time_string(item['check_in_time'])           
            check_out_time = parse_time_string(item['check_out_time'])
            total_days = (checkout_date - checkin_date).days

            full_name = request.POST.get("full_name")
            email = request.POST.get("email")
            phone = request.POST.get("phone")

            # Delivery
            delivery_instance = None
            if delivery_id and delivery_id != "Pick Up":
                try:
                    delivery_instance = Delivery.objects.get(delivery=delivery_id)
                except Delivery.DoesNotExist:
                    delivery_instance = None

            # Baby Seat
            baby_seat_instance = None
            if baby_seat_slug:
                try:
                    baby_seat_instance = BabySeat.objects.get(slug=baby_seat_slug.strip())
                except BabySeat.DoesNotExist:
                    baby_seat_instance = None

            # Racks
            rack_instance = None
            if rack_slug:
                try:
                    rack_instance = Racks_feature.objects.get(slug=rack_slug)
                except Racks_feature.DoesNotExist:
                    rack_instance = None

            now = timezone.now()
            expired_booking = Booking.objects.filter(profile__user=request.user if request.user.is_authenticated else None, created_at__lt=now - timedelta(minutes=45), payment_status="upaid")
            created_count = expired_booking.count()
            expired_booking.delete()

    
            existing_booking = Booking.objects.filter(
                car=car,
                check_in_date = checkin_date,
                check_out_date = checkout_date,
                email=email,
                profile=profile
                ).first()
            if existing_booking:
                messages.warning(request, "Booking already exists")
                return redirect('car_main:checkout', booking_id=existing_booking.booking_id)
            # Booking
            booking = Booking.objects.create(
                car=car,
                check_in_date=checkin_date,
                check_out_date=checkout_date,
                check_in_time=check_in_time,
                check_out_time=check_out_time,
                total_days=total_days,
                total_price=total_price,
                email=email,
                full_name=full_name,
                delivery_address=delivery_address,
                phone=phone,
                created_at=timezone.now(),
                profile=profile,
            )

            booking_feature = Booking_Features.objects.create(
                booking=booking,
                prepaid_fuel=prepaid_fuel,
                additional_driver=second_driver,
                flight_number=flight_number,
                delivery=delivery_instance,
                baby_seat=baby_seat_instance,
                racks=rack_instance,
            )
            print("BABY SEAT INSTANCE:", baby_seat_instance)

            # Save booking ID to session
            if 'booking' not in request.session:
                request.session['booking'] = []
            request.session['booking'].append(booking.booking_id)
            request.session.modified = True

            booking.payment_status = "unpaid"
            booking.profile = profile
            booking.save()

            messages.success(request, f'Checkout Now! Booking id is {booking.booking_id} and {car.make} {car.model}')
            return redirect('car_main:checkout', booking_id=booking.booking_id)

        messages.warning(request, "You don't have any car selections yet!")
        return redirect("/")
    else:
        messages.warning(request, "No selected car")
        return redirect("/")




def generate_booking_pdf(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)
    booking_features = Booking_Features.objects.filter(booking=booking).first()
    if request.method == 'POST':
        initials = request.POST.get('initials').strip()
        acknowledgment = request.POST.get('acknowledged') == "true"

        if not initials or not acknowledgment:
            messages.error(request, "Please fill in all required fields.")
            return JsonResponse({"error": "Please fill in all required fields."}, status=400)
        
        booking.signature = initials
        booking.acknowledged = True
        booking.agreement_uploaded = True
        booking.save()

        html_string = render_to_string('car_main/generate_pdf.html',
             {'booking': booking,
                'profile': booking.profile,
                'car': booking.car,
                'delivery': booking_features.delivery if booking_features else None,
                'baby_seat': booking_features.baby_seat if booking_features else None,
                'racks': booking_features.racks if booking_features else None,
                'check_in_date': booking.check_in_date,
                'check_out_date': booking.check_out_date,
                'check_in_time': booking.check_in_time,
                'check_out_time': booking.check_out_time,
                'total_price': booking.total_price,
                'total_days': booking.total_days,
                'delivery_address': booking.delivery_address,
                'initials': escape(initials),
                "created_at": booking.created_at,
                'acknowledged': acknowledgment,
                'request': request,
              })
        html = HTML(string=html_string)
        result = html.write_pdf()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_file:
            pdf_file.write(result)
            pdf_file.flush()
            booking.agreement_pdf.save(f"agreement_{booking_id}.pdf", pdf_file)
            booking.save()
            messages.success(request, "PDF generated successfully.")
    return JsonResponse({"success" : True})
        
    
def add_trip_to_session(request, slug):
    request.session['selection_data_obj'] = {
        'car_slug': slug,
        'car_id': request.GET.get('car_id'),
        'checkin': request.GET.get('checkin'),
        'checkout': request.GET.get('checkout'),
        'car_make': request.GET.get('car_make'),
        'car_model': request.GET.get('car_model'),
        'car_year': request.GET.get('car_year'),
        'car_total_price': request.GET.get('car_total_price'),
        'check_in_time': request.GET.get('check_in_time'),
        'check_out_time': request.GET.get('check_out_time'),
        'total_days': request.GET.get('total_days'),
    }

    request.session.modified = True

    return redirect('car_main:car_detail', slug=slug)

def update_pdf(request, booking_id):
    booking = get_object_or_404(Booking, booknig_id=booking_id)
    booking_features = Booking_Features.objects.filter(booking=booking)
    trip_images = CarPicturesForTrip.objects.filter(booking=booking)
    trip_image_urls = [request.build_absolute_uri(img.trip_image.url) for img in trip_images]

    html_string = render_to_string('car_main/generate_pdf.html', {
        'booking': booking,
        'profile': booking.profile,
        'car': booking.car,
        'delivery': booking_features.delivery if booking_features else None,
        'baby_seat': booking_features.baby_seat if booking_features else None,
        'racks': booking_features.racks if booking_features else None,
        'check_in_date': booking.check_in_date,
        'check_out_date': booking.check_out_date,
        'check_in_time': booking.check_in_time,
        'check_out_time': booking.check_out_time,
        'total_price': booking.total_price,
        'total_days': booking.total_days,
        'delivery_address': booking.delivery_address,
        'initials': escape(booking.signature or ""),
        'created_at': booking.created_at,
        'acknowledged': booking.acknowledged,
        'trip_images': trip_images,
        'trip_image_urls': trip_image_urls,
        'request': request,
    })
     
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_file:
        pdf_file.write(result)
        pdf_file.flush()
        booking.agreement_pdf.save(f"agreement_{booking_id}.pdf", pdf_file)
        booking.save()

    return JsonResponse({"success": True, "message": "PDF updated with trip images."})


@login_required
def checkout(request, booking_id):
    if not request.user.is_authenticated:
        messages.warning(request, "You must be logged in to checkout")
        return redirect("user_auths:sign-in")
    try:
        booking = Booking.objects.get(booking_id=booking_id)

        if not booking.deposit_added:
            deposit = booking.deposit
            booking_total = booking.total_price + deposit
            booking.total_price = booking_total
            booking.deposit_added = True
            booking.save()
       
        profile = Profile.objects.get(user=request.user) if request.user.is_authenticated else None
        if not profile.verified:
            redirect_url = reverse('dashboard:profile')
            # Craft a minimal HTML page that pops an alert then navigates
            html = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                <meta charset="utf-8">
                <title>Redirecting…</title>
                </head>
                <body>
                <script>
                    alert("Please upload your driver’s license in your Profile\\n"
                        + "and wait for approval to proceed with booking!");
                    window.location.href = "{redirect_url}";
                </script>
                </body>
                </html>
            """
            return HttpResponse(html)

    except Booking.DoesNotExist:
        messages.warning(request, "Booking not found")
        return redirect("/")
    try:
        booking_features = Booking_Features.objects.get(booking=booking)
    except Booking_Features.DoesNotExist:
        booking_features = None

    if request.method == "POST":
        code = request.POST.get('code')
        try:
            coupon = Coupon.objects.get(code__exact=code, active=True)

            if coupon in booking.coupons.all():
                messages.warning(request, "Coupon already applied!")
                return redirect('car_main:checkout', booking_id=booking.booking_id)
            if booking.before_discount == 0:
                booking.before_discount = booking.total_price

            if coupon.type == "Percentage":  
                discount = booking.total_price * coupon.discount / 100
            else:
                discount = min(discount, booking.total_price)
            booking.coupons.add(coupon)
            booking.total_price -= discount
            booking.saved += discount
            
            booking.save()
            messages.success(request, "Coupon applied successfully!")
            return redirect('car_main:checkout', booking_id=booking.booking_id)
        except Coupon.DoesNotExist:
            messages.warning(request, "Invalid coupon code!")
    context = {
        'booking': booking,
        'deposit': booking.deposit,
        'booking_features': booking_features,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'car_main/checkout.html', context)


@csrf_exempt
def create_checkout_session(request, booking_id):
    try:
        request_data = json.loads(request.body)
        booking = Booking.objects.get(booking_id=booking_id)
        
        stripe.api_key = settings.STRIPE_SECRET_KEY

        checkout_session = stripe.checkout.Session.create(
            customer_email=booking.email,
            payment_method_types=['card'],
            payment_intent_data={
                'metadata': {
                    "customer_name": booking.full_name or "",
                    "customer_phone": booking.phone or "",
                    "coupon_codes": ", ".join(c.code for c in booking.coupons.all()),
                    "success_id": booking.success_id,
                    "discount_saved": str(booking.saved),
                    'deposit': str(booking.deposit),
                    "booking_total": str(booking.total_price),
                }
            },
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'{booking.car.make} {booking.car.model}',
                        'images': [request.build_absolute_uri(booking.car.image.url)],
                    },
                    'unit_amount': int(booking.total_price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('car_main:payment_success', args=[booking.booking_id])) + "?session_id={CHECKOUT_SESSION_ID}&success_id="+booking.success_id+'&booking_total='+str(booking.total_price),

            cancel_url = (
                request.build_absolute_uri(
                    reverse("car_main:failed", args=[booking.booking_id])
                )
                + "?session_id={{CHECKOUT_SESSION_ID}}"
            )
        )
        booking.payment_status = "processing"
        booking.stripe_payment_intent = checkout_session['id']
        booking.save()
        print("checkout_session ==============", checkout_session)
        return JsonResponse({"sessionId": checkout_session.id})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def payment_success(request, booking_id):
    session_id = request.GET.get('session_id')
    print("Session ID:", session_id)
    booking = Booking.objects.get(booking_id=booking_id)


    # Debug the GET params
    print("GET params:", request.GET)

    if not session_id:
        messages.error(request, "Missing payment information.")
        return redirect("car_main:checkout", booking_id=booking_id)

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        payment_intent = stripe.PaymentIntent.retrieve(session.payment_intent)

        success_id = payment_intent.metadata.get("success_id")
        booking_total = payment_intent.metadata.get("booking_total")
        
        booking_total = request.GET.get('booking_total')
        print("Booking total:", booking_total)
        success_id = request.GET.get('success_id')
        print("Success ID:", success_id)

        if (
            session.payment_status == "paid" and
            Decimal(booking_total) == booking.total_price
        ):
            booking.payment_status = "paid"
            booking.stripe_payment = session_id
            booking.is_active = True
            booking.save()
            messages.success(request, "Payment successful!")
            if 'selection_data_obj' in request.session:
                del request.session['selection_data_obj']

            email_send = send_mail(
                            subject = "Booking Confirmation",
                            message = f"Hi, {booking.full_name}! Thank you for booking {booking.car} from Aspen Car Rental. Your booking starts on {booking.check_in_date} to {booking.check_out_date} with booking id {booking_id} has been confirmed. If your choose delivery option, your car will be delivered to the address: {booking.delivery_address} or pick up: {booking.car.location}. Please do not respond to this email. For any questions please contact us: +1-00000000",
                            from_email = "hello@demomailtrap.co",
                            recipient_list = [booking.email],
                        )
            if email_send:
                print("Email sent successfully.")
            else:
                print("Failed to send email.")
            email_send = send_mail(
                            subject = f'New booking {booking_id} for {booking.profile}',
                            message = f'Hi Admin! New booking {booking_id} for {booking.profile} has been confirmed. Booking details: {booking}. Booking dates are: {booking.check_in_date} to {booking.check_out_date}. Viechle details: {booking.car}. Delivery address: {booking.delivery_address}.',
                            from_email = "hello@demomailtrap.co",
                            recipient_list = ["aspencarcare@yahoo.com"]
                        )
            if email_send:
                print("Email sent successfully.")
        else:
            messages.error(request, "Payment not completed or details mismatch.")

    except Exception as e:
        messages.error(request, f"Stripe error: {str(e)}")
    context = {"booking": booking}
    return render(request, 'car_main/payment_success.html', context)



def payment_failed(request, booking_id):
    pass


@csrf_exempt
@require_http_methods(["GET"])
def update_booking_status(request, booking_id):
    today = timezone.now().date()
    booking = Booking.objects.filter(is_active=True, payment_status="paid", booking_id=booking_id)
    for b in booking:
        should_be_checked_in = b.check_in_date <= today
        if b.checked_in_tracker != should_be_checked_in:
            b.checked_in_tracker = should_be_checked_in
            b.save(update_fields=['checked_in_tracker'])

        should_be_checked_out = b.check_out_date < today
        if  b.checked_out_tracker != should_be_checked_out:
            b.checked_out_tracker = should_be_checked_out
            b.save(update_fields=['checked_out_tracker'])

            if should_be_checked_out:
                new_car_status = "Available"
            elif should_be_checked_in:
                new_car_status = "Not Available"
            else:
                new_car_status = "Available"
        
        if b.car.status!= new_car_status:
            b.car.status = new_car_status
            b.car.save(update_fields=['status'])
    return HttpResponse("Booking status updated successfully.")

