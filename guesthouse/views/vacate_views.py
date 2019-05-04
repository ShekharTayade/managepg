from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count, Q, Max
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from django.core.files.storage import FileSystemStorage

from datetime import datetime
import datetime
from django.db.models import Count, Q, Max, Sum
from decimal import Decimal

from .views import *

from .bill_views import generate_bills_for_month, get_outstanding_bills
from guesthouse.forms import Room_allocationForm, Vacate
from guesthouse.models import Guesthouse, Booking, Guest, Room_allocation
from guesthouse.models import Generate_number_by_month, Bed, Room, Floor, Block
from guesthouse.models import Room_conversion, Bed_conversion, Receipt, Bill

from guesthouse.forms import Vacate_form

today = datetime.date.today()

@login_required
def vacate_booking(request):
	
	return render(request, 'guesthouse/vacate.html', {} )

def vacate_form (request, booking_number):

	room_alloc = Room_allocation.objects.filter( booking_id = booking_number, 
		allocation_start_date__lte = today, bed_id__isnull = False	
			).select_related('booking','guest', 'bed', 'room', 'floor','block').last()		

	if not room_alloc:
		return render(request, 'guesthouse/vacate_form.html', {'room_alloc':room_alloc,
		'booking_number':booking_number} )
		
	############################################	
	## Check if any vacate process done earlier
	############################################	
	vacate = Vacate.objects.filter(room_alloc = room_alloc).first()
	# If exists, then we allow to modify the same

	if vacate:
		vacate_id = vacate.vacate_id
	else:
		vacate_id = ''
	
	unpaid_amount = 0
	adv_amount = 0
	rent = 0
	adv_rct_no = 0
	balance = 0
	payable_amount = 0
	refund_amount = 0
	
	if room_alloc.allocation_end_date:
		alloc_end_dt = room_alloc.allocation_end_date
	else :
		alloc_end_dt = today
		
	# Process the check out and get the detail amounts
	process_result = process_vacate(booking_number, alloc_end_dt)
	
	if process_result['err_flg']:
		err_flg = True
		err_msg = process_result['err_msg']
	else :
		unpaid_amount = process_result['unpaid_amount']
		adv_amount = process_result['adv_amount']
		rent = process_result['rent']
		adv_rct_no = process_result['adv_rct_no']
		balance = process_result['balance']
		payable_amount = process_result['payable_amount']
		refund_amount = process_result['refund_amount']
		rent_arrears = process_result['rent_arrears']

	if vacate:	
		vacate_form = Vacate_form(initial={'vacate_date':alloc_end_dt,
			'rent_arrears_deductions':rent_arrears}, instance=vacate)
	else:
		vacate_form = Vacate_form(initial={'vacate_date':alloc_end_dt, 
			'rent_arrears_deductions':rent_arrears})
	
	# Get outstanding bills
	result = get_outstanding_bills(request, booking_number)
	outstanding_bills = {}
	outstanding_amount = 0
	if result:
		outstanding_bills = result['outstanding_bills']
		outstanding_bills_amount = result['outstanding_amount']
	return render(request, 'guesthouse/vacate_form.html', {'form':vacate_form,
		'room_alloc':room_alloc, 'booking_number':booking_number, 'adv_amount':adv_amount,
		'rent':rent, 'adv_rct_no':adv_rct_no, 'balance':balance, 'payable_amount':payable_amount,
		'refund_amount':refund_amount, 'outstanding_bills':outstanding_bills, 
		'outstanding_bills_amount':outstanding_bills_amount, 'vacate_id':vacate_id} )

@csrf_exempt		
def set_vacate_date(request):
	err_flg = False
	err_msg = ''
	unpaid_amount = 0

	booking_number = request.POST.get('booking_number','')
	vacate_date = request.POST.get('vacate_date','')
	
	try:
		if vacate_date != '':
			alloc_end_date = datetime.datetime.strptime(vacate_date, "%Y-%m-%d").date()
			if booking_number != '':
				process_result = process_vacate(booking_number, alloc_end_date)
				if process_result['err_flg']:
					err_flg = True
					err_msg = process_result['err_msg']
				else :
					payable_amount = process_result['payable_amount']
					refund_amount = process_result['refund_amount']
					rent_arrears = process_result['rent_arrears']
			else:
				err_flg = True
				err_msg = 'BOOKING-REQUIRED'
		else:
			err_flg = True
			err_msg = 'DATE-REQUIRED'
	except ValueError :
			err_flg = True
			err_msg = 'WRONG-DATE-FORMAT'
		
	
	return JsonResponse({'err_flg':err_flg, 'err_msg':err_msg, 'payable_amount':payable_amount,
			'refund_amount':refund_amount, 'rent_arrears': rent_arrears})	
		
# Update the allocation end date / Check out date and get rent and bill charges since last bill
def process_vacate(booking_number, alloc_end_date):

	err_flg = False
	err_msg = ''
	## Set the end date for the room allocation and the booking
	room = Room_allocation.objects.filter( booking_id = booking_number, 
		bed_id__isnull = False).order_by('allocation_start_date').update(
			allocation_end_date = alloc_end_date)	
	book = Booking.objects.filter( booking_number = booking_number).update(check_out_date = alloc_end_date)


	room_alloc = Room_allocation.objects.filter( booking_id = booking_number, 
			allocation_end_date = alloc_end_date).select_related(
				'booking','guest', 'bed', 'room', 'floor','block').first()		

	booking = Booking.objects.get( booking_number = booking_number)

				
	if room_alloc.allocation_end_date:
		alloc_end_dt = room_alloc.allocation_end_date
	else :
		alloc_end_dt = today
		
	########################
	## 	Get advance details
	if room_alloc:
		adv = Receipt.objects.filter(Q(booking = room_alloc.booking) & 
			( Q(receipt_for = 'AD') |  Q(receipt_for = 'BK') )
			)

	adv_amount = 0
	adv_rct_no = ''
	if adv:
		for a in adv:
			adv_amount = adv_amount + a.amount
			adv_rct_no = a.receipt_number

	##########################
	## 	Get rent for the room
	rent = 0
	if room_alloc:
		room_conv = Room_conversion.objects.filter(room_id = room_alloc.room_id, available_from__lte = alloc_end_dt,
					available_to__gte = alloc_end_dt).first()
		if room_conv:
			if room_alloc.booking.tenure == 'LT':
				rent = room_conv.rent_per_bed
			else :
				rent = room_conv.short_term_rent_per_bed
		else:
			if room_alloc.booking.tenure == 'LT':			
				rent = room_alloc.room.rent_per_bed
			else:
				rent = room_alloc.room.short_term_rent_per_bed				

	# Check the latest bill month
	#max_month = Bill.objects.filter( booking_id = booking_number ).aggregate( max_month=Max('bill_for_month') )
	#if max_month:
	#	max_bill_month = max_month['max_month']
	#else:
	#	max_bill_month = ''
		
	# Check out Month
	year = str(alloc_end_date.year)
	mth = alloc_end_date.strftime('%m')
	alloc_end_month = year + '-' + mth
	
	# Run billing to ensure lat month billing is done.
	err_flg = generate_bills_for_month(alloc_end_month, booking_number)
	if err_flg :
		err_msg = 'A system error occured while billing for ' + booking_number + ' for month ' + alloc_end_month
	
	########################
	## 	Get net payable
	rct_types_for_billing = ['RN', 'FD', 'AR', 'OT']
	bills = Bill.objects.filter(booking_id = booking_number).aggregate(bill_sum=Sum('amount'))
	rcts = Receipt.objects.filter(booking_id = booking_number,
		receipt_for__in = rct_types_for_billing).aggregate(rct_sum=Sum('amount'))

	balance = 0
	bill_amt = 0
	rct_amt = 0
	if bills['bill_sum']:
		bill_amt = bills['bill_sum']
	if rcts['rct_sum']:
		rct_amt = rcts['rct_sum']
	balance = Decimal( bill_amt - rct_amt - adv_amount)
	rent_arrears = bill_amt - rct_amt
			
	payable_amount = 0
	refund_amount = 0	
	if balance > 0:
		payable_amount = balance
	else:
		refund_amount = balance * -1

	bill_type = ['FD','RN']
	curr_bills = Bill.objects.filter(booking_id = booking_number, 
		bill_for_month = alloc_end_month, bill_for__in = bill_type, receipt__isnull=True)
	unpaid_amount = 0
	for c in curr_bills:
		curr_rct = Receipt.objects.filter(booking_id = booking_number, 
			receipt_for_month = alloc_end_month, bill = c )
		curr_rct_amt = 0
		for cr in curr_rct:
			curr_rct_amt = curr_rct_amt + cr.amount
			
		## This is based on the fact that there will not be any receipts for Rent and Food
		## without the month for and the bill
		unpaid_amount = unpaid_amount + ( c.amount - curr_rct_amt )			

	return ({'unpaid_amount':unpaid_amount, 'err_flg':err_flg, 'err_msg':err_msg, 'adv_amount':adv_amount,
		'rent':rent, 'adv_rct_no':adv_rct_no, 'balance':balance, 'payable_amount':payable_amount,
		'refund_amount':refund_amount, 'rent_arrears':rent_arrears})
	
def vacate_confirm(request):

	valid_fail_msg = ''

	vacate_id = request.POST.get('vacate_id', '') 
	vacate = {}
	if vacate_id != '':
		vacate = Vacate.objects.get(vacate_id = vacate_id)
	
	alloc_id = request.POST.get('alloc_id', '')
	if alloc_id == '':
		valid_fail_msg = "Invalid data. Can't proceed."
		return  render(request, 'guesthouse/vacate_confirm.html', {'valid_fail_msg':valid_fail_msg} )
	room_alloc = Room_allocation.objects.get(alloc_id = alloc_id)	
		
	v_date = request.POST.get('vacate_date', '')
	if v_date == '':
		valid_fail_msg = "Invalid vacate date. Can't proceed."
		return  render(request, 'guesthouse/vacate_confirm.html', {'valid_fail_msg':valid_fail_msg} )

	vacate_date = datetime.datetime.strptime(v_date, "%Y-%m-%d").date()
	
	m_deductions = request.POST.get('maintenance_deductions', '0')
	if m_deductions == '':
		maintenance_deductions = 0
	else :
		maintenance_deductions = Decimal(m_deductions)
		
	r_deductions = request.POST.get('rent_arrears_deductions', '0')
	if r_deductions == '':
		rent_arrears_deductions = 0
	else:
		rent_arrears_deductions = Decimal(r_deductions)
		
	o_deductions = request.POST.get('other_deductions', '0')
	if o_deductions == '':
		other_deductions = 0
	else:
		other_deductions = Decimal(o_deductions)
		
	f_amount = request.POST.get('final_payable_amount', '0')
	if f_amount == '':
		final_payable_amount = 0
	else:
		final_payable_amount = Decimal(f_amount)
		
	r_amount = request.POST.get('refund_amount', '0')
	if r_amount == '':
		refund_amount = 0
	else:
		refund_amount = Decimal(r_amount)
		
	refund_mode_of_payment = request.POST.get('refund_mode_of_payment', '')
	refund_cheque_dd_no = request.POST.get('refund_cheque_dd_no', '')
	refund_cheque_dd_in_favour_of = request.POST.get('refund_cheque_dd_in_favour_of', '')
	c_date = request.POST.get('refund_cheque_dd_date', '')
	if c_date != '' :
		refund_cheque_dd_date = datetime.datetime.strptime(c_date, "%Y-%m-%d").date()
	else:
		refund_cheque_dd_date = None
	refund_bank_acc_no = request.POST.get('refund_bank_acc_no', '')
	refund_ifsc_code = request.POST.get('refund_ifsc_code', '')
	refund_bank_name = request.POST.get('refund_bank_name', '')
	refund_bank_branch = request.POST.get('refund_bank_branch', '')
	refund_reference = request.POST.get('refund_reference', '')
	statement_prepared_by = request.POST.get('statement_prepared_by', '')
	management_approval_by = request.POST.get('management_approval_by', '')
	
	advance_amount = request.POST.get('advance_amount', '')
	advance_rct_no = request.POST.get('advance_rct_no', '')
	
	if vacate:
		vac = Vacate (
			vacate_id = vacate_id,
			vacate_date = vacate_date,
			room_alloc_id = alloc_id,
			maintenance_deductions = maintenance_deductions,
			rent_arrears_deductions = rent_arrears_deductions,
			other_deductions = other_deductions,
			rental_payment_status = '',
			final_payable_amount = final_payable_amount,
			refund_amount = refund_amount,
			refund_mode_of_payment = refund_mode_of_payment,
			refund_cheque_dd_in_favour_of = refund_cheque_dd_in_favour_of,
			refund_cheque_dd_no = refund_cheque_dd_no,
			refund_cheque_dd_date = refund_cheque_dd_date,
			refund_bank_acc_no = refund_bank_acc_no,
			refund_ifsc_code = refund_ifsc_code,
			refund_bank_name = refund_bank_name,
			refund_bank_branch = refund_bank_branch,
			refund_reference = refund_reference,
			statement_prepared_by = statement_prepared_by,
			management_approval_by = management_approval_by,
			created_date = vacate.created_date,
			updated_date = today
		)
	
	else:
		vac = Vacate (
			vacate_date = vacate_date,
			room_alloc_id = alloc_id,
			maintenance_deductions = maintenance_deductions,
			rent_arrears_deductions = rent_arrears_deductions,
			other_deductions = other_deductions,
			rental_payment_status = '',
			final_payable_amount = final_payable_amount,
			refund_amount = refund_amount,
			refund_mode_of_payment = refund_mode_of_payment,
			refund_cheque_dd_in_favour_of = refund_cheque_dd_in_favour_of,
			refund_cheque_dd_no = refund_cheque_dd_no,
			refund_cheque_dd_date = refund_cheque_dd_date,
			refund_bank_acc_no = refund_bank_acc_no,
			refund_ifsc_code = refund_ifsc_code,
			refund_bank_name = refund_bank_name,
			refund_bank_branch = refund_bank_branch,
			refund_reference = refund_reference,
			statement_prepared_by = statement_prepared_by,
			management_approval_by = management_approval_by,
			created_date = today,
			updated_date = today
		)
		
	vac.save()
	
	# Close the account for the booking
	booking = Booking.objects.filter(booking_number = room_alloc.booking_id).update(account_closed = True)	
	
	# Get rent
	rent = 0
	if room_alloc:
		room_conv = Room_conversion.objects.filter(room_id = room_alloc.room_id).first()
		if room_conv:
			rent = room_conv.rent_per_bed
		else:
			rent = room_alloc.room.rent_per_bed
	
	return render(request, 'guesthouse/vacate_confirm.html', {'vacate':vac,
		'room_alloc':room_alloc, 'advance_amount':advance_amount, 
		'advance_rct_no':advance_rct_no, 'rent':rent} )
		
def vacate_print(request, vacate_id):
	vacate = {}
	vacate = Vacate.objects.get(vacate_id = vacate_id)

	room_alloc = Room_allocation.objects.get(alloc_id = vacate.room_alloc_id)

	adv = Receipt.objects.filter(booking = room_alloc.booking,
			receipt_for__in = ['AD', 'BK'])
	advance_amount = 0
	advance_rct_no = ''
	for a in adv:
		advance_amount = advance_amount + a.amount
		advance_rct_no = a.receipt_number
			
	
	# Get rent
	rent = 0
	if room_alloc:
		room_conv = Room_conversion.objects.filter(room_id = room_alloc.room_id).first()
		if room_conv:
			rent = room_conv.rent_per_bed
		else:
			rent = room_alloc.room.rent_per_bed
			
		
	html_string = render_to_string('guesthouse/vacate_print.html', {'vacate':vacate,
		'room_alloc':room_alloc, 'advance_amount':advance_amount, 
		'advance_rct_no':advance_rct_no, 'rent':rent})

	html = HTML(string=html_string, base_url=request.build_absolute_uri())
	
	html.write_pdf(target= settings.TMP_FILES + str(vacate.vacate_id) + '_pdf.pdf',
		stylesheets=[
					#CSS(settings.CSS_FILES +  'style.default.css'), 
					#CSS(settings.CSS_FILES +  'custom.css'),
					#CSS(settings.CSS_FILES +  'printpdf.css'),
					#CSS(settings.VENDOR_FILES + 'bootstrap/css/bootstrap.min.css') 
					],
						presentational_hints=True);
					
	fs = FileSystemStorage(settings.TMP_FILES)
	with fs.open(str(vacate.vacate_id) + '_pdf.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="' + str(vacate.vacate_id) + '_pdf.pdf"'
		return response

	return response		

def vacate_search_print(requets, booking_number):

	return ()
	