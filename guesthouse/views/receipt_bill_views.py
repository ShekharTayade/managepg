from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count, Q, Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta

from num2words import num2words

import json

from django.http import JsonResponse
#from weasyprint import HTML, CSS
#from django.template.loader import render_to_string
#from django.core.files.storage import FileSystemStorage

from .views import *
from guesthouse.forms import AdvReceiptForm
from guesthouse.models import Guesthouse, Booking, Guest, Room_allocation, Bill, Receipt
from guesthouse.models import Generate_number_by_month, Bed, Room, Floor, Block
from guesthouse.models import Room_allocation

from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from django.core.files.storage import FileSystemStorage

today = datetime.date.today()

def booking_details_for_payment(request, receipt_type):
	
	if receipt_type == 'AD':
		receipt_type_name = "Advance"
	if receipt_type == 'FD':
		receipt_type_name = "Food Service"
	if receipt_type == 'RN':
		receipt_type_name = "Monthly Rent "
	if receipt_type == 'AR':
		receipt_type_name = "Advance Rent "
	if receipt_type == 'BK':
		receipt_type_name = "Blocking Advance"
			
	return render(request, 'guesthouse/booking_details_for_payment.html', {
		'receipt_type_name':receipt_type_name, 'receipt_type':receipt_type})

	
@csrf_exempt	
def choose_booking_for_payment(request):
	
	booking_num = request.POST.get('booking_num','')
	first_name = request.POST.get('first_name','')
	middle_name = request.POST.get('middle_name','')
	last_name = request.POST.get('last_name','')
	receipt_type = request.POST.get('receipt_type','')
	page = request.POST.get('page', 1)
	
	#if booking_num == '' :
	#	room_alloc = {}
	#	return JsonResponse({ 'room_alloc' : room_alloc})

	bookings_list = Room_allocation.objects.all().select_related('guest', 'booking').order_by('created_date')

	count = bookings_list.count()
		
	if booking_num != '' :
		bookings_list = bookings_list.filter(booking_id = booking_num)
	if first_name != '' :
		bookings_list = bookings_list.filter(guest__first_name__iexact = first_name)
	if middle_name != '' :
		bookings_list = bookings_list.filter(guest__middle_name__iexact = middle_name)
	if last_name != '' :
		bookings_list = bookings_list.filter(guest__last_name__iexact = last_name)

	paginator = Paginator(bookings_list, 5)
	bookings = paginator.get_page(page)
	try:
		bookings = paginator.page(page)
	except PageNotAnInteger:
		bookings = paginator.page(1)
	except EmptyPage:
		bookings = paginator.page(paginator.num_pages)		
		
	return render(request, 'guesthouse/bookings_table_for_receipt.html', 
			{'bookings':bookings, 'count':count, 'receipt_type':receipt_type} )


def payment_receipt(request):	

	if request.method == 'POST':		
		alloc_id = request.GET.get('alloc_id','0')
		booking_number = request.GET.get('booking_number','')
		booking = Booking.objects.get(booking_number = booking_number)
		adv_receiptForm = AdvReceiptForm(request.POST.copy())
		receipt_type = adv_receiptForm.data['receipt_for']
		if adv_receiptForm.is_valid():
			rct = adv_receiptForm.save(commit=False)
			rct.guest = booking.guest
			rct.booking = booking

			## Get next receipt number
			rct.receipt_number = getNextReceiptNumber()

			# Save the Receipt
			rct.save()
			adv_receiptForm = AdvReceiptForm(instance = rct)
			return redirect('payment_confirmation', rct_id=rct.id)
			
	elif request.method == 'GET':		
		receipt_type = request.GET.get('receipt_type','')
		alloc_id = request.GET.get('alloc_id','0')
		booking_number = request.GET.get('booking_number','')

		if alloc_id == '' :
			alloc_id = '0'
		alloc_id = int(alloc_id)
		
		rct_for = ''
		
		adv_receiptForm = AdvReceiptForm(initial={'receipt_for':receipt_type, 'mode_of_payment':'ON',
			'receipt_date':today, })
	room_alloc = Room_allocation.objects.get(pk = alloc_id)
	booking = Booking.objects.get(booking_number = booking_number)

	'''
	if receipt_type == "RN":
		template = 'guesthouse/rent_receipt.html'
	if receipt_type == "AD":
		template = 'guesthouse/advance_receipt.html'
	if receipt_type == "AR":
		template = 'guesthouse/advance_rent_receipt.html'
	if receipt_type == "BK":
		template = 'guesthouse/blocking_advance_receipt.html'
	if receipt_type == "FD":
		template = 'guesthouse/food_receipt.html'
	if receipt_type == "OT":
		template = 'guesthouse/others_receipt.html'
	'''
	return render(request, 'guesthouse/advance_receipt.html', {'form':adv_receiptForm, 
				'room_alloc':room_alloc, 'booking':booking, 'receipt_type':receipt_type})	



def payment_confirmation(request, rct_id):

	gh = Guesthouse.objects.get(pk=settings.GH_ID)	
	rct = Receipt.objects.get(pk = rct_id)
	receipt_type = rct.get_receipt_for_display()
	
	this_date = datetime.datetime.strptime(today.strftime('%Y-%m-%d') + " 23:59:59", "%Y-%m-%d %H:%M:%S")
	
	room_alloc = Room_allocation.objects.filter(booking_id = rct.booking_id, 
		allocation_end_date__gte = this_date).first()
	if not room_alloc:
		room_alloc = Room_allocation.objects.filter(booking_id = rct.booking_id, 
			allocation_end_date__isnull = True).first()
	
	amount = num2words(rct.amount)
	
	return render(request, 'guesthouse/payment_confirmation.html', {'rct':rct,
		'gh':gh, 'room_alloc':room_alloc, 'amount':amount, 'receipt_type':receipt_type})		

		
def payment_confirmation_pdf(request, rct_id):
	gh = Guesthouse.objects.get(pk=settings.GH_ID)	
	rct = Receipt.objects.get(pk = rct_id)
	receipt_type = rct.get_receipt_for_display()
	
	this_date = datetime.datetime.strptime(today.strftime('%Y-%m-%d') + " 23:59:59", "%Y-%m-%d %H:%M:%S")
	
	room_alloc = Room_allocation.objects.filter(booking_id = rct.booking_id, 
		allocation_end_date__gte = this_date).first()
	if not room_alloc:
		room_alloc = Room_allocation.objects.filter(booking_id = rct.booking_id, 
			allocation_end_date__isnull = True).first()
	
	amount = num2words(rct.amount)

		
	html_string = render_to_string('guesthouse/payment_confirmation_pdf.html', {'rct':rct,
	'gh':gh, 'room_alloc':room_alloc, 'amount':amount, 'receipt_type':receipt_type})

	html = HTML(string=html_string, base_url=request.build_absolute_uri())
	
	html.write_pdf(target= settings.TMP_FILES + rct.receipt_number + '_pdf.pdf',
		stylesheets=[
					#CSS(settings.CSS_FILES +  'style.default.css'), 
					#CSS(settings.CSS_FILES +  'custom.css'),
					#CSS(settings.CSS_FILES +  'printpdf.css'),
					#CSS(settings.VENDOR_FILES + 'bootstrap/css/bootstrap.min.css') 
					],
						presentational_hints=True);
					
	fs = FileSystemStorage(settings.TMP_FILES)
	with fs.open(rct.receipt_number + '_pdf.pdf') as pdf:
		response = HttpResponse(pdf, content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="' + rct.receipt_number + '_pdf.pdf"'
		return response

	return response		

		

def getNextReceiptNumber():
	booking_num = 0
	#Get curentyear, month in format YYYYMM
	dt = datetime.datetime.now()
	mnth = dt.strftime("%Y%m")

	# Get an suffix required 
	guesthouse = Guesthouse.objects.get(gh_id = settings.GH_ID)
	suffix = guesthouse.month_year_suffix
	
	monthyear = Generate_number_by_month.objects.filter(type='RECEIPT-NUMBER', month_year = mnth).first()
	if monthyear :
		booking_num = monthyear.current_number + 1
	else :
		booking_num = 1
		
	# Update generated number in DB
	num = Generate_number_by_month(
		type = 'RECEIPT-NUMBER',
		month_year = mnth,
		current_number = booking_num
		)
	
	num.save()
		
	generated_num = 0
	if suffix:
		generated_num = (mnth + suffix + str(booking_num))
	else:
		generated_num = (mnth + str(booking_num))
	return generated_num 	
	
	
def print_receipts(request):
	
	return render(request, 'guesthouse/print_receipts.html', {} )
	
	
@csrf_exempt
def get_receipts(request):
	startDt = ''
	endDt = ''
	booking_number = ''
	
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

	receipt_number = request.POST.get("receipt_number", '')	

	
	rcts_list = Receipt.objects.all().select_related('guest', 'booking').order_by('created_date')
	
	if startDt:
		rcts_list = rcts_list.filter(created_date__gte = startDt)
	if endDt:
		rcts_list = rcts_list.filter(created_date__lte = endDt)

	if f_name:
		rcts_list = rcts_list.filter(guest__first_name__iexact = f_name)
	if m_name:
		rcts_list = rcts_list.filter(guest__middle_name__iexact = m_name)
	if l_name:
		rcts_list = rcts_list.filter(guest__last_name__iexact = l_name)

	
	if email_id:
		rcts_list = rcts_list.filter(guest__email_id__iexact = email_id)
	if phone_number:
		rcts_list = rcts_list.filter(guest__phone_number__iexact = phone_number)


	if receipt_number:
		rcts_list = rcts_list.filter(receipt_number__iexact = receipt_number)
	
	
	count = rcts_list.count()

	paginator = Paginator(rcts_list, 5)
	receipts = paginator.get_page(page)
	try:
		receipts = paginator.page(page)
	except PageNotAnInteger:
		receipts = paginator.page(1)
	except EmptyPage:
		receipts = paginator.page(paginator.num_pages)
	
	return render(request, 'guesthouse/receipts_table.html', {'count':count, 
		'receipts': receipts})		