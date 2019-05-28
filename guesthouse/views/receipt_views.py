from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count, Q, Max, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta
from django.contrib.auth.decorators import login_required
from num2words import num2words

import json

from django.http import JsonResponse
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from django.core.files.storage import FileSystemStorage

from .views import *
from guesthouse.views import bill_views

from guesthouse.forms import AdvReceiptForm, AdvReceiptForm_AR, ReceiptForm
from guesthouse.models import Guesthouse, Booking, Guest, Room_allocation, Bill, Receipt
from guesthouse.models import Generate_number_by_month, Bed, Room, Floor, Block
from guesthouse.models import Room_allocation, Room_conversion

from guesthouse.views import user_is_manager

today = datetime.date.today()

@login_required
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
@login_required	
def choose_booking_for_payment(request):

	room_name = request.POST.get('room_name','')
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
		
	if room_name != '' :
		bookings_list = bookings_list.filter(room__room_name = room_name)
	if booking_num != '' :
		bookings_list = bookings_list.filter(booking_id = booking_num)
	if first_name != '' :
		bookings_list = bookings_list.filter(guest__first_name__iexact = first_name)
	if middle_name != '' :
		bookings_list = bookings_list.filter(guest__middle_name__iexact = middle_name)
	if last_name != '' :
		bookings_list = bookings_list.filter(guest__last_name__iexact = last_name)

	count = bookings_list.count()

	paginator = Paginator(bookings_list, 5)
	#bookings = paginator.get_page(page)
	try:
		bookings = paginator.page(page)
	except PageNotAnInteger:
		bookings = paginator.page(1)
	except EmptyPage:
		bookings = paginator.page(paginator.num_pages)		
		
	return render(request, 'guesthouse/bookings_table_for_receipt.html', 
			{'bookings':bookings, 'count':count, 'receipt_type':receipt_type} )

@login_required
def payment_receipt(request):	

	if request.method == 'POST':		
		alloc_id = request.GET.get('alloc_id','0')
		booking_number = request.GET.get('booking_number','')
		booking = Booking.objects.get(booking_number = booking_number)
		receipt_type = request.POST.get('receipt_type', '')
		if receipt_type == 'AR':
			adv_receiptForm = AdvReceiptForm_AR(request.POST.copy())
			#Get the 4 months for which advance rent receipt is to be generated
			month1 = adv_receiptForm.data['receipt_for_month1']
			month2 = adv_receiptForm.data['receipt_for_month2']
			month3 = adv_receiptForm.data['receipt_for_month3']
			month4 = adv_receiptForm.data['receipt_for_month4']
		
			## Create 4 receipts for the 4 month advance
			rct_ids = []
			receipt_number = getNextReceiptNumber()				
			
			if month1 != '':
				r = Receipt(
					receipt_number = receipt_number,
					receipt_date = adv_receiptForm.data['receipt_date'],
					receipt_for = 'AR',
					guest = booking.guest, 
					booking = booking,
					bill = None,
					receipt_for_month = month1,
					amount = float(adv_receiptForm.data['amount']) / 4,
					mode_of_payment = adv_receiptForm.data['mode_of_payment'],
					payment_reference = adv_receiptForm.data['payment_reference'],
					created_date = today,
					updated_date = today
				)
				r.save()
				rct_ids.append(r.id)
			if month2 != '':
				r = Receipt(
					receipt_number = receipt_number,
					receipt_date = adv_receiptForm.data['receipt_date'],
					receipt_for = 'AR',
					guest = booking.guest, 
					booking = booking,
					bill = None,
					receipt_for_month = month2,
					amount = float(adv_receiptForm.data['amount']) / 4,
					mode_of_payment = adv_receiptForm.data['mode_of_payment'],
					payment_reference = adv_receiptForm.data['payment_reference'],
					created_date = today,
					updated_date = today
				)
				r.save()		
				rct_ids.append(r.id)
			if month3 != '':
				r = Receipt(
					receipt_number = receipt_number,
					receipt_date = adv_receiptForm.data['receipt_date'],
					receipt_for = 'AR',
					guest = booking.guest, 
					booking = booking,
					bill = None,
					receipt_for_month = month3,
					amount = float(adv_receiptForm.data['amount']) / 4,
					mode_of_payment = adv_receiptForm.data['mode_of_payment'],
					payment_reference = adv_receiptForm.data['payment_reference'],
					created_date = today,
					updated_date = today
				)
				r.save()		
				rct_ids.append(r.id)
			if month4 != '':
				r = Receipt(
					receipt_number = receipt_number,
					receipt_date = adv_receiptForm.data['receipt_date'],
					receipt_for = 'AR',
					guest = booking.guest, 
					booking = booking,
					bill = None,
					receipt_for_month = month4,
					amount = float(adv_receiptForm.data['amount']) / 4,
					mode_of_payment = adv_receiptForm.data['mode_of_payment'],
					payment_reference = adv_receiptForm.data['payment_reference'],
					created_date = today,
					updated_date = today
				)
				r.save()		
				rct_ids.append(r.id)
			
				return redirect('payment_confirmation_AR', rct_no=receipt_number)
		else:
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
		if receipt_type == 'AR':
		
			#Get current month + 3 for populating adv months
			
			# Month 1
			year = str(today.year)
			mth = today.strftime('%m')
			month1 = year + '-' + mth
			
			# Month 2
			if mth == '12' :
				mth = '01'
				year = str(int(year) + 1)
			else:
				mth = str(int(mth) + 1)
			month2_dt = today.replace(month=int(mth))
			mth = month2_dt.strftime('%m')
			month2 = year + '-' + mth
			
			# Month 3
			if mth == '12' :
				mth = '01'
				year = str(int(year) + 1)
			else:
				mth = str(int(mth) + 1)
			month3_dt = month2_dt.replace(month=int(mth))
			mth = month3_dt.strftime('%m')
			month3 = year + '-' + mth
 		
			# Month 4
			if mth == '12' :
				mth = '01'
				year = str(int(year) + 1)
			else:
				mth = str(int(mth) + 1)
			month4_dt = month3_dt.replace(month=int(mth))
			mth = month4_dt.strftime('%m')
			month4 = year + '-' + mth


			adv_receiptForm_AR = AdvReceiptForm_AR(initial={'receipt_for':receipt_type, 'mode_of_payment':'ON',
				'receipt_date':today, 'receipt_for_month1':month1, 'receipt_for_month2':month2,
				'receipt_for_month3':month3, 'receipt_for_month4':month4})
		else:
			adv_receiptForm = AdvReceiptForm(initial={'receipt_for':receipt_type, 'mode_of_payment':'ON',
				'receipt_date':today, })
	try: 		
		room_alloc = Room_allocation.objects.get(pk = alloc_id)
	except Room_allocation.DoesNotExist:
		room_alloc = {}
		
	booking = Booking.objects.get(booking_number = booking_number)

	try:
		room_conv = Room_conversion.objects.get(room_id = room_alloc.room_id)
	except Room_conversion.DoesNotExist:
		room_conv = {}
		
	if room_conv:
		rent = room_conv.rent_per_bed
	else:
		rent = room_alloc.room.rent_per_bed
	
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
	if receipt_type == 'AR':
		template = 'guesthouse/payment_receipt_AR.html'
		return render(request, template, {'form':adv_receiptForm_AR, 
					'room_alloc':room_alloc, 'booking':booking, 'receipt_type':receipt_type,
					'room_conv':room_conv})	
	else:
		template = 'guesthouse/payment_receipt.html'
		
		return render(request, template, {'form':adv_receiptForm, 
					'room_alloc':room_alloc, 'booking':booking, 'receipt_type':receipt_type,
					'rent':rent})	


@login_required
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

	
	if rct.receipt_for == 'FD':
		template = 'guesthouse/payment_confirmation_food.html'
	else :
		template = 'guesthouse/payment_confirmation.html'
	
	return render(request, template, {'rct':rct,
		'gh':gh, 'room_alloc':room_alloc, 'amount':amount, 'receipt_type':receipt_type})		

@login_required		
def payment_confirmation_AR(request, rct_no):
	gh = Guesthouse.objects.get(pk=settings.GH_ID)	
	rcts = Receipt.objects.filter(receipt_number = rct_no)
	
	rct = rcts.first()
	receipt_type = rct.get_receipt_for_display()
	
	this_date = datetime.datetime.strptime(today.strftime('%Y-%m-%d') + " 23:59:59", "%Y-%m-%d %H:%M:%S")
	
	room_alloc = Room_allocation.objects.filter(booking_id = rct.booking_id, 
		allocation_end_date__gte = this_date).first()
	if not room_alloc:
		room_alloc = Room_allocation.objects.filter(booking_id = rct.booking_id, 
			allocation_end_date__isnull = True).first()
	
	amount = num2words(rct.amount*4)
	
	return render(request, 'guesthouse/payment_confirmation_AR.html', {'rct':rct, 'rcts':rcts, 
		'gh':gh, 'room_alloc':room_alloc, 'amount':amount, 'receipt_type':receipt_type})		
	
@login_required		
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
	
	if rct.receipt_for == 'FD':
		template = 'guesthouse/payment_confirmation_pdf_food.html'
	else:
		template = 'guesthouse/payment_confirmation_pdf.html'
		
	html_string = render_to_string(template, {'rct':rct,
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

@login_required
def payment_confirmation_pdf_AR(request, rct_no):
	gh = Guesthouse.objects.get(pk=settings.GH_ID)	
	rcts = Receipt.objects.filter(receipt_number = rct_no)
	rct = rcts.first()
	receipt_type = rct.get_receipt_for_display()
	
	this_date = datetime.datetime.strptime(today.strftime('%Y-%m-%d') + " 23:59:59", "%Y-%m-%d %H:%M:%S")
	
	room_alloc = Room_allocation.objects.filter(booking_id = rct.booking_id, 
		allocation_end_date__gte = this_date).first()
	if not room_alloc:
		room_alloc = Room_allocation.objects.filter(booking_id = rct.booking_id, 
			allocation_end_date__isnull = True).first()
	
	amount = num2words(rct.amount*4)

		
	html_string = render_to_string('guesthouse/payment_confirmation_pdf_AR.html', {'rct':rct, 
	'rcts':rcts,'gh':gh, 'room_alloc':room_alloc, 'amount':amount, 'receipt_type':receipt_type})

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
	
@login_required	
def print_receipts(request):
	
	return render(request, 'guesthouse/print_receipts.html', {} )
	
	
@csrf_exempt
@login_required
def get_receipts(request):
	startDt = ''
	endDt = ''
	booking_number = ''
	receipt_number = ''
	
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
	booking_number = request.POST.get("booking_number", '')	

	
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
		rcts_list = rcts_list.filter(receipt_number = receipt_number)
	if booking_number:
		rcts_list = rcts_list.filter(booking_id = booking_number)
	
	
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

@csrf_exempt
def get_net_advance( request):

	booking_number = request.POST.get('booking_number', '')
	if booking_number == '':
		return JsonResponse({'net_adv_amt':0, 'adv_amt':0})
		
	adv_rct = Receipt.objects.filter(booking_id = booking_number, 
		receipt_for = 'AD').aggregate(Sum('amount'))
	blk_rct = Receipt.objects.filter(booking_id = booking_number, 
		receipt_for = 'BK').aggregate(Sum('amount'))
	
	this_date = datetime.datetime.strptime(today.strftime('%Y-%m-%d') + " 23:59:59", "%Y-%m-%d %H:%M:%S")
	room_alloc = Room_allocation.objects.filter(booking_id = booking_number).order_by('updated_date').last()
	
	#Net advance amount to be collected = Adv Amount for the room - already paid - blocking amount
	r_adv_amt = 0
	adv_amt = 0
	if room_alloc:
		rent = 0
		rent_adv = bill_views.get_room_adv_rent(room_alloc.alloc_id)			
		adv_amt = rent_adv['advance']	
		r_adv_amt = rent_adv['advance']	
		'''
		room = Room.objects.filter( available_from__lte = today,
			available_to__gte = today, room_ = room_alloc.room_id,
			rates_effective_from__lte = today, rates_effective_to__gte = today ).first()
		
		room_conv = Room_conversion.objects.filter( available_from__lte = today,
			available_to__gte = today, room_id = room_alloc.room_id,
			rates_effective_from__lte = today, rates_effective_to__gte = today ).first()
			
		if room_conv :
			if room_alloc.booking.tenure == 'LT':
				r_adv_amt = room_conv.advance 
				adv_amt = room_conv.advance
			else :
				r_adv_amt = room_conv.short_term_advance 
				adv_amt = room_conv.short_term_advance
		else:
			if room_alloc.booking.tenure == 'LT':
				if room:
					r_adv_amt = room.advance 
					adv_amt = room.advance
			else :
				if room: 
					r_adv_amt = room.short_term_advance 
					adv_amt = room.short_term_advance
	'''
	if adv_rct['amount__sum']:
		adv_amt = adv_amt - adv_rct['amount__sum']
	if blk_rct['amount__sum']:
		adv_amt = adv_amt - blk_rct['amount__sum']
	if adv_amt < 0:
		adv_amt =0
		
	return JsonResponse({'net_adv_amt':adv_amt, 'adv_amt':r_adv_amt })	

@csrf_exempt	
def get_monthly_adv_rent(request):
	booking_number = request.POST.get('booking_number', '')
	if booking_number == '':
		return JsonResponse({'adv_rent_with_disc':0})
		
	this_date = datetime.datetime.strptime(today.strftime('%Y-%m-%d') + " 23:59:59", "%Y-%m-%d %H:%M:%S")
	room_alloc = Room_allocation.objects.filter(booking_id = booking_number, 
		allocation_end_date__gte = this_date).first()
	if not room_alloc:
		room_alloc = Room_allocation.objects.filter(booking_id = booking_number, 
			allocation_end_date__isnull = True).first()
	
	booking = Booking.objects.get(booking_number = booking_number)
	if booking.tenure == 'ST':
		return JsonResponse({'adv_rent_with_disc':0})

	# Check for room conversion
	room_conv = Room_conversion.objects.filter(room_id = room_alloc.room_id,
			available_from__lte = today, available_to__gte = today).first()
	if room_conv:
		rent = room_conv.rent_per_bed
	else:
		rent = room_alloc.room.rent_per_bed
		
	# 5% discount while paying advance rent for 4 months
	adv_rent_with_disc = round(rent - ( rent * 5 /100))

	return JsonResponse({'adv_rent_with_disc':adv_rent_with_disc})
	
@login_required
@user_is_manager
def receipt_modify(request, rct_id):

	rct = Receipt.objects.get(pk=rct_id)
	
	room_alloc = Room_allocation.objects.filter(booking_id = rct.booking_id).order_by('updated_date').last()
		
	form = ReceiptForm(request.POST or None, instance=rct)
	if form.is_valid():
		form.save()
		return redirect(reverse('payment_confirmation',  kwargs={ 'rct_id': rct_id }))

	return render(request, 'guesthouse/receipt_modify.html', {'form': form, 'room_alloc':room_alloc,
	'receipt_type':rct.receipt_for}) 

@csrf_exempt
def get_receipt(request):

	rct_id = request.POST.get('rct_id', '')
	rct = Receipt.objects.get(pk=rct_id)
	room_alloc = Room_allocation.objects.filter(booking_id = rct.booking_id).order_by('updated_date').last()

	return render(request, 'guesthouse/receipt_delete_confirm_modal.html', {'room_alloc':room_alloc,
	'rct':rct}) 

@csrf_exempt
@user_is_manager
def delete_receipt(	request):

	rct_id = request.POST.get('rct_id', '')
	status = 'SUCCESS'
	try:
		rct = Receipt.objects.get(pk=rct_id)
		rct_no = rct.receipt_number
		rct.delete()
	except Receipt.DoesNotExist:
		status = 'NO-RECEIPT'
		
	return JsonResponse({'status':status, 'rct_no':rct_no})