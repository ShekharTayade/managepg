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
from guesthouse.models import Generate_number_by_month, Billing_error


## Checks if the vacation period ends in the current month 
## and return the number of vacation days
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
		# Check if vacation period ends in current month
		if v.end_date >= curr_month_1st and v.end_date <= month_end_date:
					
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

	month_rent = 0
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
	
	food_tax = get_taxes('FOOD')

	if booking.food_option :
		food_pref = booking.food_preference
		price = Food_price.objects.get(type = food_pref)
		food_charge = price.price + (price.price * food_tax / 100)   # 5% GST
	
		# Exception handling for vacation period
		vacation_days = get_vacation_days(month, booking_number)
		if vacation_days >= 28 :
			food_charge = price.vacation_period_price + (vacation_period_price * food_tax / 100)   # 5% GST

		idx = month.find("-")		
		year_num = int(month[:idx])
		month_num = int(month[(idx+1):])
		month_days = calendar.monthrange(year_num, month_num)[1]
		month_end_date = datetime.datetime.strptime(month + '-' + str(month_days), "%Y-%m-%d").date()
		
		rooms = Room_allocation.objects.filter(booking_id = booking_number)
		rooms = rooms.filter(
			Q(allocation_end_date__isnull = True) | Q(allocation_end_date__gte = curr_month_1st ) )
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
					# Take the full month food charge
					food_charge = food_charge
				else :
					# Take partial month food charge
					food_charge =  (food_charge/month_days) * curr_month_rent_days	
			
	return food_charge   ## Including tax
	
def get_advance_rent_month(month, booking_number):
	curr_month_1st =  datetime.datetime.strptime(month + '-01', "%Y-%m-%d").date()
	
	booking = Booking.objects.get(booking_number = booking_number)
	if not booking:
		return 0
	
	rct = Receipt.objects.filter(booking_id = booking_number, receipt_for_month = month, receipt_for='AR')
	adv_receipt_amt = 0
	for r in rct:
		adv_receipt_amt = adv_receipt_amt + r.amount
	
	return adv_receipt_amt
		

@csrf_exempt
def get_bills_for_month(request):
	
	booking_number = request.POST.get('booking_number','')
	bill_for_month = request.POST.get('bill_for_month','')
	receipt_for = request.POST.get('receipt_for','')
	bills = Bill.objects.filter(booking_id = booking_number, 
			bill_for_month = bill_for_month, bill_for = receipt_for).values('bill_number', 'amount')
	
	return JsonResponse({'bills':list(bills)}, safe=False)	
	
	

def generate_curr_month_bills():	
	err_flag = False
	today = datetime.datetime.today()
	
	year = str(today.year)
	mth = today.strftime('%m')
	month = year + '-' + mth
	curr_month_1st =  datetime.datetime.strptime(month + '-01', "%Y-%m-%d").date()
	# Get all bookings valid during the current month
	bookings = Booking.objects.filter( 
		Q(check_out_date__isnull = True) | Q(check_out_date__gte = curr_month_1st) )
	
	for b in bookings:
		#############################################
		# GENERATE RENT BILL
		#############################################
		try:
			rent = get_rent_for_month(month, b.booking_number)
			# Check if any rent is already paid
			rct = Receipt.objects.filter(booking_id = b.booking_number, receipt_for_month = month, receipt_for = 'RN')
			rent_paid = 0
			for r in rct:
				rent_paid = rent_paid + r.amount
				
			# Check if any advance rent paid
			adv_rent = get_advance_rent_month(month, b.booking_number)

			net_rent = rent - rent_paid - adv_rent
			if net_rent < 0:
				net_rent = 0
			if net_rent > 0:
				# Check if rent bill is already generated
				rn_bill = Bill.objects.filter(bill_for_month = month, 
					bill_for = 'RN', booking = b, guest = b.guest)
				# Generate the bill only if not already generated
				if not rn_bill:				
					bill_number = get_next_bill_number()
					rent_bill = Bill(
						bill_number = bill_number,
						bill_date = today,
						bill_for_month = month, 
						guest = b.guest,
						booking = b,
						bill_for = 'RN',
						amount = net_rent,
						created_date = datetime.datetime.now(),
						updated_date = datetime.datetime.now()	
					)
					rent_bill.save()
			
		except Exception as error:
			err_flag = True
			print (error)
			err = Billing_error (
				bill_number = bill_number,
				bill_date = today,
				bill_for_month = month,
				guest = b.guest,
				booking = b,
				bill_for = 'RN',
				amount = food_charges,
				error = error,
				created_date = datetime.datetime.now(),
				updated_date = datetime.datetime.now()		
			)
			err.save()

		#############################################
		# GENERATE FOOD BILL
		#############################################
		try:
			food_charges = get_food_charges_for_month(month, b.booking_number)
			
			# Check if any food charges are already paid
			rct = Receipt.objects.filter(booking_id = b.booking_number, receipt_for_month = month, receipt_for = 'FD')
			fdrct = 0
			if rct :
				for r in rct:
					fdrct = fdrct + r.amount
			
			food_charges = food_charges - fdrct
			if food_charges > 0:	
				# Check if food bill is already generated
				fd_bill = Bill.objects.filter(bill_for_month = month, 
					bill_for = 'FD', booking = b, guest = b.guest)
				# Generate the bill only if not already generated
				if not fd_bill:				
					bill_number = get_next_bill_number()
					food_bill = Bill(
						bill_number = bill_number,
						bill_date = today,
						bill_for_month = month, 
						guest = b.guest,
						booking = b,
						bill_for = 'FD',
						amount = food_charges,
						created_date = datetime.datetime.now(),
						updated_date = datetime.datetime.now()	
					)	
					
					food_bill.save()
		except Exception as error:
			err_flag = True
			print (error)
			err = Billing_error (
				bill_number = bill_number,
				bill_date = today,
				bill_for_month = month,
				guest = b.guest,
				booking = b,
				bill_for = 'FD',
				amount = food_charges,
				error = error,
				created_date = datetime.datetime.now(),
				updated_date = datetime.datetime.now()		
			)
			err.save()

			
	return 	err_flag
		

def get_next_bill_number():
	bill_num = 0
	#Get curentyear, month in format YYYYMM
	dt = datetime.datetime.now()
	mnth = dt.strftime("%Y%m")

	# Get an suffix required 
	guesthouse = Guesthouse.objects.get(gh_id = settings.GH_ID)
	suffix = guesthouse.month_year_suffix
	
	monthyear = Generate_number_by_month.objects.filter(type='BILL-NUMBER', month_year = mnth).first()
	if monthyear :
		bill_num = monthyear.current_number + 1
	else :
		bill_num = 1
		
	# Update generated number in DB
	num = Generate_number_by_month(
		type = 'BILL-NUMBER',
		description = "Billing number generation",
		month_year = mnth,
		current_number = bill_num
		)
	
	num.save()
		
	generated_num = 0
	if suffix:
		generated_num = (mnth + suffix + str(bill_num))
	else:
		generated_num = (mnth + str(bill_num))
	return generated_num 	
	

def get_taxes(type):

	taxes = Tax.objects.filter(effective_from__lte = today,  effective_to__gte = today,
				name = type).first()
				
	tax_rate = 0
	if taxes:
		tax_rate = taxes.tax_rate
	return ({"tax_rate":tax_rate})
	