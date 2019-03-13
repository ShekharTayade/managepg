from django.shortcuts import render,redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count, Q, Max

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta
import calendar

from django.http import JsonResponse

from .views import *
from guesthouse.models import Guesthouse, Booking, Guest, Room_allocation, Bill, Receipt

def get_rent_for_month(month, booking_number):

	curr_month_1st =  datetime.datetime.strptime(month + '-01', "%Y-%m-%d")
	
	booking = Booking.objects.get(booking_number = booking_number)
	if not booking:
		return 0
	
	rooms = Room_allocation.objects.filter(booking_id = booking_number)
	rooms = rooms.filter(
		Q(allocation_end_date__isnull = True) | Q(allocation_end_date__gte = curr_month_1st ) )
	
	if not rooms :
		return 0

	idx = month.find("-")
	
	year_num = int(month[:idx])
	month_num = int(month[(idx+1):])
	month_days = calendar.monthrange(year_num, month_num)[1]
	month_end_date = datetime.datetime.strptime(month + '-' + str(month_days) + ' 23:59:59', "%Y-%m-%d %H:%M:%S")
	
	month_rent  = 0
	for r in rooms:
		# if allocation ends on 1st or later of this month, then proceed
		if r.allocation_end_date.date() >= curr_month_1st.date() and r.allocation_start_date.date() <= month_end_date.date():
			# If allocaiton started before current month, then take start day as 1, else
			# take start day as the date on which it starts in current month
			if r.allocation_start_date.date() <= curr_month_1st.date():
				start_day = 1
			elif r.allocation_start_date.date() > curr_month_1st.date() and r.allocation_start_date.date() <= month_end_date.date() :	
				start_day = r.allocation_start_date.day
			
			# If allocation ends before end of this month, then take last day as the date 
			# on which it ends, else take last day of the month as end date
			if r.allocation_end_date.date() < month_end_date.date():
				end_day = r.allocation_start_date.day
			else :
				end_day = month_end_date.day
				
			curr_month_rent_days = end_day - start_day
			
			if r.allocation_end_date.date() >= month_end_date.date() :
				# Take the full month rent
				month_rent =  month_rent + r.room.rent_per_bed
			else :
				# Take partial month rent
				month_rent = month_rent + (r.room.rent_per_bed/month_days) * curr_month_rent_days
			
			
	return month_rent
		