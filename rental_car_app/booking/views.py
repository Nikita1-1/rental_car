from datetime import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from car.models import *
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from car.views import *
# Create your views here.

def calculate_total_price(checkin_date, checkout_date, car):

    try:
        total_days=(checkout_date - checkin_date).days

        if total_days <= 1:
            total_days = 1
        else:
            total_days += 1
        total_price = total_days * car.price
        return total_price
    except Exception as e:
        return 0,0

@csrf_exempt
def check_car_availability(request):

    if request.method == "POST":
        checkin = request.POST.get('checkin')
        checkout = request.POST.get('checkout')
        time_in = request.POST.get('time_in')
        time_out = request.POST.get('time_out')

        check_in_date = datetime.strptime(checkin, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(checkout, '%Y-%m-%d').date()
        check_in_time = datetime.strptime(time_in, '%H:%M').time()
        check_out_time = datetime.strptime(time_out, '%H:%M').time()

        total_price = 0

        available_cars = Car.objects.all()
        for c in available_cars:
            individual_price = c.price

        available_cars = [
            car for car in available_cars
            if all(booking.is_available(check_in_date, check_out_date) for booking in car.bookings.all())
        ]

        for car in available_cars:
            car_total_price = calculate_total_price(check_in_date, check_out_date, car)
            car.total_price = car_total_price
            

        if not available_cars:
            return render(request, 'car_main/home.html', {
                'error': "No cars available for the selected dates."
            })
            
        return render(request, 'car_main/available_cars.html', {
            "individual_price": individual_price,
            'available_cars': available_cars,
            'checkin': check_in_date,
            'checkout': check_out_date,
            'time_in': check_in_time,
            'time_out': check_out_time,
            'total_price': car_total_price,
        })

def add_to_selection(request):
    delivery= request.POST['delivery']

    car_selection = {
        'car_id': request.POST['car_id'],
        'car_slug': request.POST['car_slug'],
        'make': request.POST['car_make'],
        'model': request.POST['car_model'],
        'year': request.POST['car_year'],
        'total_price': request.POST['total_price'],
        'checkin': request.POST['checkin'],
        'checkout': request.POST['checkout'],
        'delivery': delivery,
        'flight_number': request.POST['flight_number'],
        'prepaid_fuel': request.POST['prepaid_fuel'] == 'True',
        'second_driver': request.POST['second_driver'] == 'True',
        'baby_seat': request.POST['baby_seat'],
        'rack': request.POST['rack'],
        'check_in_time': request.POST['check_in_time'],
        'check_out_time': request.POST['check_out_time'],
    }

    if delivery.startswith('Delivery to you'):
        car_selection['address'] = request.POST.get('address', '')

    print('car_selection', car_selection)
    if 'selection_data_obj' in request.session:
        request.session['selection_data_obj'] = car_selection  # Update with the new car selection
    else:
        request.session['selection_data_obj'] = car_selection  # Initialize with the first car selection

    data = {
        'success': True,
        'data': request.session['selection_data_obj'],
        'total_selected_items': len(request.session['selection_data_obj'])
    }
    return JsonResponse(data)


def booking_info(request, slug):
    # Retrieve car from slug (to use in the context)
    car = get_object_or_404(Car, slug=slug)

    # Retrieve data from the session (assuming you store it in the session via the AJAX request)
    if 'selection_data_obj' in request.session:
        selected_car = request.session['selection_data_obj']
        

        if not selected_car:
            return JsonResponse({'success': False, 'message': 'No car selected.'}, status=400)
    else:
        return JsonResponse({'success': False, 'message': 'No selection data found.'}, status=400)

    
    rack_obj = None
    if selected_car.get('rack'):
        try:
            rack_obj = Racks_feature.objects.get(slug=selected_car.get('rack'))
        except Racks_feature.DoesNotExist:
            rack_obj = None
    
    baby_seat_obj = None
    if selected_car.get('baby_seat'):
        try:
            baby_seat_obj = BabySeat.objects.get(slug=selected_car.get('baby_seat'))
        except BabySeat.DoesNotExist:
            baby_seat_obj = None

    context = {
        'car': car,
        'selected_car': selected_car,  # Include selected car data in the context
        'checkin': selected_car.get('checkin', ''),
        'checkout': selected_car.get('checkout', ''),
        'total_price': selected_car.get('total_price', ''),
        'delivery': selected_car.get('delivery', 'Pick Up'),
        'flight_number': selected_car.get('flight_number', ''),
        'prepaid_fuel': selected_car.get('prepaid_fuel', False),
        'second_driver': selected_car.get('second_driver', False),
        'baby_seat': baby_seat_obj,
        'rack': rack_obj,
        'delivery_address': selected_car.get('address', ''),
        

    }
    print('selected_car', selected_car)
    return render(request, 'car_main/booking.html', context)

def delete_session(request):
    request.session.pop('selection_data_obj', None)
    return redirect(request.META.get("HTTP_REFERER"))


def delete_selection(request):
    car_id = request.GET.get('car_id')
    if 'selection_data_obj' in request.session:
        selection_data = request.session['selection_data_obj']
        if car_id in selection_data:
            del selection_data[car_id]
            request.session['selection_data_obj'] = selection_data
            return JsonResponse({'success': True, 'message': 'Car removed from selection.'})
    return JsonResponse({'success': False, 'message': 'Car not found in selection.'})