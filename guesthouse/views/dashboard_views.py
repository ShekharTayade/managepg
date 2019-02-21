from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count, Q, Max
from django.conf import settings

from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta

import json

from django.http import JsonResponse

from .views import *
from guesthouse.forms import BookingForm, GuestForm, Room_allocationForm
from guesthouse.models import Guesthouse, Booking, Guest, Room_allocation 
from guesthouse.models import Generate_number_by_month, Bed, Room, Floor, Block

today = datetime.datetime.today()

def get_dashboard_data(request):

	capacity = Bed.objects.all().order_by('block', 'floor', 'room', 'bed')
	occupancy = Bed.objects.filter(
			bed__isnull = False, allocation_end_date__gte = today
			).order_by('block', 'floor', 'room', 'bed')
			
	return JsonResponse({'capcity':capacity, 'occupancy':occupancy})	