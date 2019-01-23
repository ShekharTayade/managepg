from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count

from datetime import datetime
import datetime
import json

from .views import *
from guesthouse.forms import BookingForm, GuestForm
from guesthouse.models import Guesthouse, Booking, Guest

today = datetime.date.today()

def booking(request):

	return render(request, "guesthouse/booking1.html", {} )
	

def booking_form(request):
 
	if request.method == 'POST':
		form = BookingForm(request.POST, request.FILES)
		booking = Booking.objects.get(booking_number = form.booking_number)

		if form.is_valid():
			booking = form.save(commit=False)
			booking.booking_number = getNextBookingNum()
			booking.save()
			return redirect('booking')
	else:
		booking_form = BookingForm()
		guest_form = GuestForm()
	return render(request, 'guesthouse/booking.html', {
		'booking_form': booking_form, 'guest_form': guest_form })

	
