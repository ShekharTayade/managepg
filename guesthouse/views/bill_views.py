from django.shortcuts import render,redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count, Q, Max, Sum
from django.db.models import ProtectedError
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse

from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta
import calendar
from decimal import Decimal

from django.http import JsonResponse

from .views import *
from guesthouse.models import Guesthouse, Booking, Guest, Room_allocation, Bill, Room_conversion
from guesthouse.models import Receipt, Food_price, Vacation_period, Tax, Closing_balance
from guesthouse.models import Generate_number_by_month, Billing_error, Month_closing_error
from guesthouse.models import Dormitory_conf
from guesthouse.forms import BillForm

from guesthouse.views import user_is_manager

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
		#if allocation start date is null then we don't generate bill
		if not r.allocation_start_date:
			continue
		# If allocation end date is null, then let's set end date to a long period so it get considered for
		# current month
		if not r.allocation_end_date:
			allocation_end_date = datetime.datetime.strptime("2999-12-31", "%Y-%m-%d").date()
		else :
			allocation_end_date = r.allocation_end_date
		
		# if allocation ends on 1st or later of this month, then proceed
		if allocation_end_date >= curr_month_1st and r.allocation_start_date <= month_end_date:
					
			# If allocation started before current month, then take start day as 1, else
			# take start day as the date on which it starts in current month
			if r.allocation_start_date <= curr_month_1st:
				start_day = 1
			elif r.allocation_start_date > curr_month_1st and r.allocation_start_date <= month_end_date :
				start_day = r.allocation_start_date.day
			
			# If allocation ends before end of this month, then take last day as the date 
			# on which it ends, else take last day of the month as end date
			if allocation_end_date < month_end_date:
				end_day = allocation_end_date.day
			else :
				end_day = month_end_date.day
				
			curr_month_rent_days = end_day - start_day + 1

			##########################
			## 	Get rent for the room			
			rent = 0
			rent_adv = get_room_adv_rent(r.alloc_id)
			rent = rent_adv['rent']	
							
			if r.allocation_start_date <= curr_month_1st and allocation_end_date >= month_end_date :
				# Take the full month rent
				month_rent =  month_rent + rent
			else :
				# Take partial month rent
				month_rent = month_rent + (rent/month_days) * curr_month_rent_days
			
			## Check is any advance rent is paid (AR rent receipt) for the current month.
			## If so, we deduct 5% from the month rent
			adv_rent_rct = Receipt.objects.filter(booking_id = r.booking_id, receipt_for_month = month, receipt_for='AR')
			if adv_rent_rct:
				month_rent = month_rent - (month_rent * 5 / 100)
				
		# If booking is not valid for current month, then no billing
		else:
			month_rent = 0
			
	return round(month_rent)
	
def get_food_charges_for_month(month, booking_number):
	curr_month_1st =  datetime.datetime.strptime(month + '-01', "%Y-%m-%d").date()

	booking = Booking.objects.get(booking_number = booking_number)
	if not booking:
		return 0
	
	food_charge = 0
	
	food_tax = get_taxes('FOOD')

	if booking.food_option :
		food_pref = booking.food_preference
		try:
			price = Food_price.objects.get(type = food_pref)
			food_charge = price.price + (price.price * food_tax / 100)   # 5% GST
		except Food_price.DoesNotExist:
			food_charge = 0
			err_flag = True
			print (error)
			err = Billing_error (
				bill_number = None,
				bill_date = today,
				bill_for_month = month,
				guest = booking.guest,
				booking = booking,
				bill_for = 'FD',
				amount = food_charges,
				error = 'Food Price Error- Food Pref: ' + food_pref,
				created_date = datetime.datetime.now(),
				updated_date = datetime.datetime.now()		
			)
			err.save()
			
			
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
			#if allocation start date is null then we don't generate bill
			if not r.allocation_start_date:
				continue
				
			# If allocation end date is null, then let's set end date to a long period so it get considered for
			# current month
			if not r.allocation_end_date:
				allocation_end_date = datetime.datetime.strptime("2999-12-31", "%Y-%m-%d").date()
			else :
				allocation_end_date = r.allocation_end_date

			# if allocation ends on 1st or later of this month, then proceed
			if allocation_end_date >= curr_month_1st and r.allocation_start_date <= month_end_date:
						
				# If allocaiton started before current month, then take start day as 1, else
				# take start day as the date on which it starts in current month
				if r.allocation_start_date <= curr_month_1st:
					start_day = 1
				elif r.allocation_start_date > curr_month_1st and r.allocation_start_date <= month_end_date :
					start_day = r.allocation_start_date.day
				
				# If allocation ends before end of this month, then take last day as the date 
				# on which it ends, else take last day of the month as end date
				if allocation_end_date < month_end_date:
					end_day = allocation_end_date.day
				else :
					end_day = month_end_date.day
					
				curr_month_rent_days = end_day - start_day + 1
				
				if r.allocation_start_date <= curr_month_1st and allocation_end_date >= month_end_date :
					# Take the full month food charge
					food_charge = food_charge
				else :
					# Take partial month food charge	
					food_charge =  (food_charge/month_days) * curr_month_rent_days	

			# No food bill if booking not valid in the current month
			else:
				food_charge = 0
	return round(food_charge)   ## Including tax
	
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
	

def generate_month_bills(month):
	err_flag = False

	###############################################
	# Generate bill only after Mar 2019
	###############################################
	if month <= "2019-03":
		return err_flag
		
	today = datetime.datetime.today()
	
	if month == '':
		year = str(today.year)
		mth = today.strftime('%m')
		month = year + '-' + mth
	curr_month_1st =  datetime.datetime.strptime(month + '-01', "%Y-%m-%d").date()
	# Get all bookings valid during the current month
	bookings = Booking.objects.filter( 
			Q(check_out_date__isnull = True) | Q(check_out_date__gte = curr_month_1st) 
		)
	
	for b in bookings:
		#############################################
		# GENERATE RENT BILL
		#############################################
		# Check if bill is already generated for current month
		c_bill = Bill.objects.filter(booking_id = b.booking_number, bill_for_month = month,
				bill_for = 'RN')
		
		# Generates bill only if not already generated
		if True:
			#c_bill.count() == 0 :	
			try:
				rent = get_rent_for_month(month, b.booking_number)

				# Check if any advance rent paid
				#adv_rent = get_advance_rent_month(month, b.booking_number)

				net_rent = rent
				if net_rent > 0:
					# Check if rent bill is already generated
					rn_bill = Bill.objects.filter(bill_for_month = month, 
						bill_for = 'RN', booking = b, guest = b.guest).last()
					# Generate the bill if not already generated, else update it
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
					else:
						bill_number = rn_bill.bill_number
						rent_bill = Bill(
							bill_number = rn_bill.bill_number,
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
					amount = net_rent,
					error = error,
					created_date = datetime.datetime.now(),
					updated_date = datetime.datetime.now()		
				)
				err.save()

		#############################################
		# GENERATE FOOD BILL
		#############################################

		# Check if bill is already generated for current month
		f_bill = Bill.objects.filter(booking_id = b.booking_number, bill_for_month = month,
				bill_for = 'FD')
		
		# Generates bill only if not already generated
		if f_bill.count() == 0 :
			try:
				food_charges = get_food_charges_for_month(month, b.booking_number)
				
				# Check if any food charges are already paid
				if food_charges > 0:
					# Check if food bill is already generated
					fd_bill = Bill.objects.filter(bill_for_month = month, 
						bill_for = 'FD', booking = b, guest = b.guest).last()
					# Generate the bill if not already generated, else update
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
					else:
						bill_number = fd_bill.bill_number
						food_bill = Bill(
							bill_number = fd_bill.bill_number,
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

	#########################################################################################
	# This will update advacne rent receipts for current month with the respective bill that
	# is generated this month
	#########################################################################################
	match_advance_rent(month)
			
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

	today = datetime.datetime.today().date()

	taxes = Tax.objects.filter(effective_from__lte = today,  effective_to__gte = today,
				name = type).first()
				
	tax_rate = 0
	if taxes:
		tax_rate = taxes.tax_rate
	return (tax_rate)



def process_month_closing(month):
	today = datetime.datetime.today()

	# If no month is provided, default to the current month
	if month == '':
		year = str(today.year)
		mth = today.strftime('%m')
		month = year + '-' + mth


	# Generate Bills for current month
	err_flag = False
	bill_generation = generate_month_bills(month)
	if bill_generation == True:		
		return ("An Error Occured in Billing")


	##########################################
	###### The closing is for previous month
	##########################################
	prev_month = datetime.datetime.strptime(month + '-01', "%Y-%m-%d").date() + relativedelta(months=-1)
	## Set month to the previous month
	month = datetime.datetime.strftime(prev_month, "%Y-%m")
	
	## 1st of the month to be processed
	curr_month_1st =  datetime.datetime.strptime(month + '-01', "%Y-%m-%d").date()

	# Get all bookings valid during the  month
	bookings = Booking.objects.filter( 
		Q(check_out_date__isnull = True) | Q(check_out_date__gte = curr_month_1st) )
	
	rct_types_for_billing = ['RN', 'FD', 'AR', 'OT']  # not considering the advance paid for the monthly calculations
	for b in bookings:

		# Check if closing is already done for the month, booking
		curr_cls = Closing_balance.objects.filter(booking = b, closing_balance_month = month)
		
		# perform closing only if not already done
		if curr_cls == 0:
			bills = Bill.objects.filter(booking = b).aggregate(bill_sum=Sum('amount'))
			rcts = Receipt.objects.filter(
				booking = b, receipt_for__in = rct_types_for_billing).aggregate(rct_sum=Sum('amount'))
			
			if bills['bill_sum'] and rcts['rct_sum']:
				balance = Decimal( bills['bill_sum'] - rcts['rct_sum'] )
			else:
				balance = Decimal(0)
			
			# update the closing balance as of the month
			try:
				closing = Closing_balance(
					guest = b.guest,
					booking = b,
					closing_balance_month = month,
					amount = balance,
					created_date = today,	
					updated_date = today
				)
				closing.save()
			except Exception as error:
				err_flag = True
				print (error)
				err = Month_closing_error (
					guest = b.guest,
					booking = b,
					closing_balance_month = month,
					amount = closing_balance,
					error = error,
					created_date = today,	
					updated_date = today
				)
				err.save()	
	return err_flag


def generate_bills_for_month(month, booking_number):
	
	err_flag = False
	###############################################
	# Generate bill only after Mar 2019
	###############################################
	if month <= "2019-03":
		return err_flag


	today = datetime.datetime.today()
	
	if month == '':
		year = str(today.year)
		mth = today.strftime('%m')
		month = year + '-' + mth
	curr_month_1st =  datetime.datetime.strptime(month + '-01', "%Y-%m-%d").date()
	
	# Get all bookings valid during the current month
	booking = Booking.objects.filter( Q( booking_number = booking_number) &
			( Q(check_out_date__isnull = True) | Q(check_out_date__gte = curr_month_1st) )
		).first()	
		
	# Check if bill is already generated for current month
	c_bill = Bill.objects.filter(booking = booking, bill_for_month = month,
			bill_for = 'RN')

	#############################################
	# GENERATE RENT BILL
	#############################################
	# Generates bill only if not already generated
	if True:
		#c_bill.count() == 0 :	
		try:
			rent = get_rent_for_month(month, booking_number)

			'''
			# Check if any rent is already paid
			rct = Receipt.objects.filter(booking_id = booking.booking_number, receipt_for_month = month, receipt_for = 'RN')
			rent_paid = 0
			bill_number = ''
			for r in rct:
				rent_paid = rent_paid + r.amount	

			# Check if any advance rent paid
			adv_rent = get_advance_rent_month(month, booking.booking_number)

			net_rent = rent - rent_paid - adv_rent
			'''
			net_rent = rent
			
			if net_rent < 0:
				net_rent = 0
			
			if net_rent > 0:
				# Check if rent bill is already generated
				rn_bill = Bill.objects.filter(bill_for_month = month, 
					bill_for = 'RN', booking = booking, guest = booking.guest).last()
				# Generate the bill if not already generated, else update it
				if not rn_bill:				
					bill_number = get_next_bill_number()
					rent_bill = Bill(
						bill_number = bill_number,
						bill_date = today,
						bill_for_month = month, 
						guest = booking.guest,
						booking = booking,
						bill_for = 'RN',
						amount = net_rent,
						created_date = datetime.datetime.now(),
						updated_date = datetime.datetime.now()	
					)
				else:
					rent_bill = Bill(
						bill_number = rn_bill.bill_number,
						bill_date = today,
						bill_for_month = month, 
						guest = booking.guest,
						booking = booking,
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
				guest = booking.guest,
				booking = booking,
				bill_for = 'RN',
				amount = net_rent,
				error = error,
				created_date = datetime.datetime.now(),
				updated_date = datetime.datetime.now()		
			)
			err.save()

	#############################################
	# GENERATE FOOD BILL
	#############################################
	# Check if bill is already generated for current month
	f_bill = Bill.objects.filter(booking = booking, bill_for_month = month,
			bill_for = 'FD')

	# Generates bill only if not already generated
	if True:
		#f_bill.count() == 0 :
		try:
			food_charges = get_food_charges_for_month(month, booking.booking_number)
			'''
			# Check if any food charges are already paid
			rct = Receipt.objects.filter(booking_id = booking.booking_number, receipt_for_month = month, receipt_for = 'FD')
			fdrct = 0
			bill_number = ''
			if rct :
				for r in rct:
					fdrct = fdrct + r.amount
			
			food_charges = food_charges - fdrct
			'''
			if not food_charges:
				food_charges = 0
				
			if food_charges > 0:	
				# Check if food bill is already generated
				fd_bill = Bill.objects.filter(bill_for_month = month, 
					bill_for = 'FD', booking = booking, guest = booking.guest).last()
				# Generate the bill only if not already generated
				if not fd_bill:				
					bill_number = get_next_bill_number()
					food_bill = Bill(
						bill_number = bill_number,
						bill_date = today,
						bill_for_month = month, 
						guest = booking.guest,
						booking = booking,
						bill_for = 'FD',
						amount = food_charges,
						created_date = datetime.datetime.now(),
						updated_date = datetime.datetime.now()	
					)	
				else:
					food_bill = Bill(
						bill_number = fd_bill.bill_number,
						bill_date = today,
						bill_for_month = month, 
						guest = booking.guest,
						booking = booking,
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
				guest = booking.guest,
				booking = booking,
				bill_for = 'FD',
				amount = food_charges,
				error = error,
				created_date = datetime.datetime.now(),
				updated_date = datetime.datetime.now()		
			)
			err.save()
	
	return 	err_flag
	
def get_outstanding_bills(request, booking_number):
	
	rcts = Receipt.objects.filter(booking_id = booking_number, bill_id__isnull = False).values_list('bill_id', flat=True)
	outstanding_bills = Bill.objects.filter(booking_id = booking_number).exclude(bill_number__in = rcts)
	total_amount = outstanding_bills.aggregate(amt=Sum('amount'))
	outstanding_amount = 0
	if total_amount:
		outstanding_amount = total_amount['amt']
	return ({'outstanding_bills':outstanding_bills, 'outstanding_amount':outstanding_amount})
	

# Generate bills for current and all previous months, where bill is not generated
def generate_bills(request, month):
	
	return ()
	
def match_advance_rent(month):

	bills = Bill.objects.filter(bill_for_month = month, bill_for = 'RN')
	
	for b in bills:
		rct = Receipt.objects.filter(receipt_for_month = month, receipt_for = 'AR',
				booking_id = b.booking_id, guest_id = b.guest_id).update(bill = b)
				
	return ()
	
	
@login_required	
def print_bills(request):
	
	return render(request, 'guesthouse/print_bills.html', {} )
	
	
@csrf_exempt
@login_required
def get_bills(request):
	startDt = ''
	endDt = ''
	booking_number = ''
	bill_number = ''
	
	page = request.POST.get('page', 1)

	from_date = request.POST.get("fromdate", '')
	if from_date != '' :
		startDt = datetime.datetime.strptime(from_date + " 23:59:59", "%Y-%m-%d %H:%M:%S")	
	to_date = request.POST.get("todate", '')
	if to_date != '' :
		endDt = datetime.datetime.strptime(to_date + " 23:59:59", "%Y-%m-%d %H:%M:%S")

	f_name = request.POST.get("f_name", '')
	m_name = request.POST.get("m_name", '')
	l_name = request.POST.get("l_name", '')
	
	email_id = request.POST.get("email_id", '')
	phone_number = request.POST.get("phone_number", '')

	bill_number = request.POST.get("bill_number", '')	
	booking_number = request.POST.get("booking_number", '')	

	
	bills_list = Bill.objects.all().select_related('guest', 'booking').order_by('created_date')
	
	if startDt:
		bills_list = bills_list.filter(created_date__gte = startDt)
	if endDt:
		bills_list = bills_list.filter(created_date__lte = endDt)

	if f_name:
		bills_list = bills_list.filter(guest__first_name__iexact = f_name)
	if m_name:
		bills_list = bills_list.filter(guest__middle_name__iexact = m_name)
	if l_name:
		bills_list = bills_list.filter(guest__last_name__iexact = l_name)
	
	if email_id:
		bills_list = bills_list.filter(guest__email_id__iexact = email_id)
	if phone_number:
		bills_list = bills_list.filter(guest__phone_number__iexact = phone_number)

	if bill_number:
		bills_list = bills_list.filter(bill_number = bill_number)
	if booking_number:
		bills_list = bills_list.filter(booking_id = booking_number)
	
	count = bills_list.count()

	paginator = Paginator(bills_list, 5)
	try:
		bills = paginator.page(page)
	except PageNotAnInteger:
		bills = paginator.page(1)
	except EmptyPage:
		bills = paginator.page(paginator.num_pages)
	
	return render(request, 'guesthouse/bills_table.html', {'count':count, 
		'bills': bills})		
		
@csrf_exempt
def get_bill(request):

	bill_number = request.POST.get('bill_number', '')
	bill = Bill.objects.get(pk=bill_number)
	
	room_alloc = Room_allocation.objects.filter(booking_id = bill.booking_id).order_by('updated_date').last()

	return render(request, 'guesthouse/bill_delete_confirm_modal.html', {'room_alloc':room_alloc,
	'bill':bill}) 

@csrf_exempt
@user_is_manager
def delete_bill(request):

	bill_number = request.POST.get('bill_number', '')
	status = 'SUCCESS'
	try:
		bill = Bill.objects.get(pk=bill_number)
		bill_number = bill.bill_number
		bill.delete()
	except Bill.DoesNotExist:
		status = 'NO-RECEIPT'
	except ProtectedError:
		status = 'RCT-EXISTS'
		
	return JsonResponse({'status':status, 'bill_number':bill_number})

@login_required
def bills_for_booking(request, month, booking_number):

	err_flag =  (month, booking_number) 
	
	if err_flag:
		msg = "An error occured while billing. Please contact support team"
	else:
		msg = "Bills generated successfully for booking number " + booking_number + ", for " + month + " month."

	return render(request, 'guesthouse/generte_bill_for_booking.html', {'err_flag':err_flag,
		'msg':msg} )

@login_required
@user_is_manager
def bill_form(request, bill_number):

	bill = Bill.objects.get(pk=bill_number)
	
	room_alloc = Room_allocation.objects.filter(booking_id = bill.booking_id).order_by('updated_date').last()
		
	form = BillForm(request.POST or None, instance=bill)
	if form.is_valid():
		form.save()
		return redirect(reverse('bill_modify_confirmation',  kwargs={ 'bill_number': bill_number }))

	return render(request, 'guesthouse/bill_form.html', {'form':form, 'room_alloc':room_alloc,
	'bill_type':bill.bill_for})

@login_required
@user_is_manager
def bill_modify_confirmation(request, bill_number):
	bill = Bill.objects.get(pk=bill_number)
	form = BillForm(instance=bill)
	return render(request, 'guesthouse/bill_modify_confirmation.html', {'form':form})

		
@login_required	
@user_is_manager
def bills_for_month(request):
	return render(request, 'guesthouse/generate_bills.html')

@csrf_exempt
@user_is_manager
def generate_bill_month(request):	
	status = ''
	msg = ''
	month = request.POST.get("month", '')
	if month == '':
		status = "01"
		msg = "Invalid month: " + month 
		return JsonResponse({'status':status, 'msg':msg}, safe=False)
	 
	err_flag = generate_month_bills(month)
	if err_flag == True:		
		status = "XX"
		msg = "An Error Occured while Billing"
	else:
		status = "00"
		msg = "Bill generation completed for " + month 
		
	return JsonResponse({'status':status, 'msg':msg}, safe=False)
	
	
def get_room_adv_rent(alloc_id):

	rent = 0
	advance = 0
	
	r = Room_allocation.objects.get(alloc_id = alloc_id)

	r_conv = Room_conversion.objects.filter(room_id = r.room_id, 
			available_from__lte = r.allocation_start_date).last()
	if r:	
		if r_conv:
			if r.booking.tenure == 'LT':
				rent = r.room.rent_per_bed
				advance = r_conv.advance
			else: 
				rent = r_conv.short_term_rent_per_bed
				advance = r_conv.short_term_advance			
		else:
			try:
				d = Dormitory_conf.objects.get(room_id = 1, bed_id = r.bed_id)
			except Dormitory_conf.DoesNotExist:
				d = None
			if r.booking.tenure == 'LT':
				if r.room_id == 1:   ## If it's dormitory
					if d:
						rent = d.rent_per_bed
						advance = d.advance
					else:
						advance = r.room.advance
						rent = r.room.rent_per_bed						
				else:
					advance = r.room.advance
					rent = r.room.rent_per_bed
			else:
				if r.room_id == 1:   ## If it's dormitory
					if d:
						rent = d.short_term_rent_per_bed
						advance = d.short_term_advance
					else:
						advance = r.room.advance
						rent = r.room.rent_per_bed												
				else:
					rent = r.room.short_term_rent_per_bed
					advance = r.room.short_term_advance
	
	return ({'rent':rent, 'advance':advance})	