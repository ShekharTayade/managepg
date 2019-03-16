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
from guesthouse.models import Guesthouse, Booking, Guest, Room_allocation, Bill
from guesthouse.models import Receipt, Food_price, Vacation_period

def get_vacation_days(month, booking_number):
	curr_month_1st =  datetime.datetime.strptime(month + '-01', "%Y-%m-%d").date()
	
	booking = Booking.objects.get(booking_number = booking_number)
	if not booking:
		return 0

	vacation_days = 0
	idx = month.find("-")
	
	year_num = int(month[:idx])
	month_num = int(month[(idx+1):])
	month_days = calendar.monthrange(year_num, month_num)[1]
	month_end_date = datetime.datetime.strptime(month + '-' + str(month_days), "%Y-%m-%d").date()
	
	vac = Vacation_period.objects.filter(booking_id = booking_number)
	
	for v in vac:
		# Check if vacation period falls in current month
		if v.end_date >= curr_month_1st and v.start_date <= month_end_date:
					
			# If vacation started before current month, then take start day as 1, else
			# take start day as the date on which it starts in current month
			if v.start_date <= curr_month_1st:
				start_day = 1
			elif v.start_date > curr_month_1st and v.start_date <= month_end_date :
				start_day = v.start_date.day
			
			# If vacation ends before end of this month, then take last day as the date 
			# on which it ends, else take last day of the month as end date
			if v.end_date < month_end_date:
				end_day = v.end_date.day
			else :
				end_day = month_end_date.day
				
			vacation_days = vacation_days + (end_day - start_day + 1)
			
	return vacation_days	
	

def get_rent_for_month(month, booking_number):

	curr_month_1st =  datetime.datetime.strptime(month + '-01', "%Y-%m-%d").date()
	
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
	month_end_date = datetime.datetime.strptime(month + '-' + str(month_days), "%Y-%m-%d").date()

	month_rent  = 0
	for r in rooms:
		# if allocation ends on 1st or later of this month, then proceed
		if r.allocation_end_date >= curr_month_1st and r.allocation_start_date <= month_end_date:
					
			# If allocaiton started before current month, then take start day as 1, else
			# take start day as the date on which it starts in current month
			if r.allocation_start_date <= curr_month_1st:
				start_day = 1
			elif r.allocation_start_date > curr_month_1st and r.allocation_start_date <= month_end_date :
				start_day = r.allocation_start_date.day
			
			# If allocation ends before end of this month, then take last day as the date 
			# on which it ends, else take last day of the month as end date
			if r.allocation_end_date < month_end_date:
				end_day = r.allocation_end_date.day
			else :
				end_day = month_end_date.day
				
			curr_month_rent_days = end_day - start_day + 1
			
			if r.allocation_start_date <= curr_month_1st and r.allocation_end_date >= month_end_date :
				# Take the full month rent
				month_rent =  month_rent + r.room.rent_per_bed
			else :
				# Take partial month rent
				month_rent = month_rent + (r.room.rent_per_bed/month_days) * curr_month_rent_days
	
	return month_rent
	
def get_food_charges_for_month(month, booking_number):
	curr_month_1st =  datetime.datetime.strptime(month + '-01', "%Y-%m-%d").date()
	
	booking = Booking.objects.get(booking_number = booking_number)
	if not booking:
		return 0
	
	food_charge = 0
	
	if booking.food_option :
		food_pref = booking.food_preference
		price = Food_price.objects.get(type = food_pref)
		food_charge = price.price + 150   # 150 is GST
	
	# Exception handling for vacation period
	vacation_days = get_vacation_days(month, booking_number)
	if vacation_days >= 15 :
		food_charge = 1286 + 64
	
	return food_charge
	
def get_advance_rent_month(month, booking_number, month_rent):
	curr_month_1st =  datetime.datetime.strptime(month + '-01', "%Y-%m-%d").date()
	
	booking = Booking.objects.get(booking_number = booking_number)
	if not booking:
		return 0
	
	rct = Receipt.objects.filter(booking_id = booking_number, receipt_for_month = month)
	adv_receipt_amt = 0
	for r in rct:
		# Check if there was any advance rent paid
		if r.receipt_for == 'AR':
			rct_amt = r.amount
			month_rent_disc = month_rent - (month_rent * 5/100)	## 5% discount for advance month rent
			if rct_amt < month_rent_disc:
				adv_receipt_amt = month_rent_disc - rct_amt
			else :
				adv_receipt_amt = 0
	
	return adv_receipt_amt
	

@csrf_exempt
def get_bills_for_month(request):
	
	booking_number = request.POST.get('booking_number','')
	bill_for_month = request.POST.get('bill_for_month','')
	receipt_for = request.POST.get('receipt_for','')
	bills = Bill.objects.filter(booking_id = booking_number, 
			bill_for_month = bill_for_month, bill_for = receipt_for).values('bill_number', 'amount')
	
	return JsonResponse({'bills':list(bills)}, safe=False)	
	
	
	
