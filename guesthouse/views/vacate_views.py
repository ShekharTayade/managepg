from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count, Q, Max
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from datetime import datetime
import datetime

from .views import *
from guesthouse.forms import Room_allocationForm
from guesthouse.models import Guesthouse, Booking, Guest, Room_allocation
from guesthouse.models import Generate_number_by_month, Bed, Room, Floor, Block
from guesthouse.models import Room_conversion, Bed_conversion

from guesthouse.forms import Vacate_form

today = datetime.date.today()

@login_required
def vacate_booking(request):
	
	return render(request, 'guesthouse/vacate.html', {} )

def vacate_form (request, booking_number):

	room_alloc = Room_allocation.objects.filter( Q(booking_id = booking_number) &
			(Q( allocation_end_date__gt = today, bed_id__isnull = False) |
			Q(allocation_end_date__isnull = True, bed_id__isnull = False))	
			).select_related('booking','guest', 'bed', 'room', 'floor','block').first()		

	vacate_form = Vacate_form(initial={'vacate_date':today})

	return render(request, 'guesthouse/vacate_form.html', {'form':vacate_form,
		'room_alloc':room_alloc, 'booking_number':booking_number} )
	