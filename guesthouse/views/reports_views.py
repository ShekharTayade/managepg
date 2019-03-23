from django.shortcuts import render,redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count, Q, Max, Sum
from django.contrib.auth.decorators import login_required
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

@login_required
def bills_receipts_report(request):


	'''
	bills = Bill.objects.filter(booking__account_closed = False).annotate(rct_amt=Sum('receipt__amount'))
	unpaid_bills = bill.filter(Q(rct_amt = None) | Q(amount__gt = F('rct_amt']))
	
	rcts_without_bills = Receipt.objects.filter(bill = None, booking__account_closed = False)
	'''
	
	booking_list = Booking.objects.filter(account_closed = False).values('booking_number','guest__first_name',
		'guest__middle_name','guest__last_name', 'check_in_date', 'check_out_date', 'guest__phone_number',
		'guest__email_id')
	
	bookings_bill = Booking.objects.filter(account_closed = False).values('booking_number','guest__first_name',
		'guest__middle_name','guest__last_name', 'check_in_date', 'check_out_date', 'guest__phone_number',
		'guest__email_id').annotate(bill_amt=Sum('bill__amount'))
		
	bookings_rct = Booking.objects.filter(account_closed = False).values('booking_number','guest__first_name',
		'guest__middle_name','guest__last_name', 'check_in_date', 'check_out_date', 'guest__phone_number',
		'guest__email_id').annotate(rct_amt=Sum('receipt__amount'))	

		
	results = {}
	
	for b in booking_list:
		results={'booking_number': b.booking_number}
		bill_rec = {}
		b_amt = 0
		rct_rec = {}
		r_amt = 0
		
		for bill in bookings_bill:
			if b.booking_number == bill.booking_id:
				b_amt = b_amt + bill.amount
		bill_rec = {'BILL-AMT':b_amt}
		
		for rct in bookings_rct:
			if b.booking_number == rct.booking_id:
				r_amt = r_amt + rct.amount
		rct_rec = {'RCT-AMT':r_amt}
		
		
		outstanding = 'TBD'
		
	
	return render(request, 'guesthouse/bills_receipts_report.html', {'bookings':bookings, 
			'outstanding':outstanding})
	
	