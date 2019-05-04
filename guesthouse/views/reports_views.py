from django.shortcuts import render,redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count, Q, Max, Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta
import calendar
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse

from guesthouse.decorators import user_is_manager

from .views import *
from guesthouse.models import Guesthouse, Booking, Guest, Room_allocation, Bill
from guesthouse.models import Receipt, Food_price, Vacation_period, Block, Floor
from guesthouse.models import Generate_number_by_month, Billing_error, Bills_receipts_dashboard
from guesthouse.models import Room_conversion, Bed_conversion, Room, Bed, Occupancy_dashboard

today = datetime.datetime.today()

@login_required		
def room_occupancy_report(request):

	beds_master = Bed.objects.filter(available_from__lte = today,
			available_to__gte = today).select_related('block','floor','room').order_by(
				'block','floor','room')

	total_rooms = Room.objects.filter(available_from__lte = today,
			available_to__gte = today).select_related('block','floor').order_by(
				'block','floor').order_by('block','floor','room_id')
				
	room_conv = Room_conversion.objects.filter(available_from__lte = today,
			available_to__gte = today).select_related('block','floor').values_list(
				'room_id', flat=True).order_by('room_id')

	bed_conv = Bed_conversion.objects.filter(available_from__lte = today,
			available_to__gte = today).select_related('block','floor','room').order_by(
				'block','floor','room') 
	
	bed_alloc = Room_allocation.objects.filter(
			Q(allocation_start_date__lte = today) &
			( Q(allocation_end_date__gt = today, bed_id__isnull = False) |
			Q(allocation_end_date__isnull = True, bed_id__isnull = False) )
		).select_related('block','floor','room').values_list('bed_id', flat=True).order_by('bed')

	bed_blocked = Room_allocation.objects.filter(
			Q(allocation_start_date__gt = today) &
			( Q(allocation_end_date__gt = today, bed_id__isnull = False) |
			Q(allocation_end_date__isnull = True, bed_id__isnull = False) )
		).select_related('block','floor','room').values_list('bed_id', flat=True).order_by('bed')
	
	Occupancy_dashboard.objects.all().delete()

	for tr in total_rooms:

		if tr.room_id in room_conv:
			beds = bed_conv.filter(room_id = tr.room_id)
		else:
			beds = beds_master.filter(room_id = tr.room_id)
				
		for b in beds:
		
			tenure = ''
			booking = Room_allocation.objects.filter(
				Q(allocation_start_date__lte = today) &
				( Q(allocation_end_date__gt = today, bed_id = b.bed_id) |
				Q(allocation_end_date__isnull = True, bed_id = b.bed_id) ) ).values('booking_id').last()

			if booking:
				term = Booking.objects.filter(booking_number = booking['booking_id']).values('tenure').last()
				if term:
					tenure = term['tenure']
		
			if b.bed_id in bed_alloc:
				alloc = True
				blocked = False
			else:
				alloc = False
			
			if b.bed_id in bed_blocked:
				alloc = False
				blocked = True
			else:
				blocked = False
							
			dashboard = Occupancy_dashboard(
				bed_id = b.bed_id,
				room_id = tr.room_id,
				floor = tr.floor,
				block = tr.block,
				occupied = alloc,
				tenure = tenure,
				blocked = blocked,
				created_date = today
			)
			dashboard.save()
	
	occupancy_dashboard = Occupancy_dashboard.objects.all().order_by('block','floor','room', 'bed')
	lt_occ_beds = Occupancy_dashboard.objects.filter(occupied = True, tenure = 'LT').order_by('block','floor','room', 'bed')
	st_occ_beds = Occupancy_dashboard.objects.filter(occupied = True, tenure = 'ST').order_by('block','floor','room', 'bed')
	blkd_beds = Occupancy_dashboard.objects.filter(blocked = True).order_by('block','floor','room', 'bed')
	
	blocks_total = Occupancy_dashboard.objects.values(
			'block__block_name').annotate(total_beds=Count('bed')).order_by('block__block_name') 
	blocks_occ = Occupancy_dashboard.objects.filter(occupied = True).values(
			'block__block_name').annotate(occupied_beds=Count('bed')).order_by('block__block_name')
	lt_blocks_occ = Occupancy_dashboard.objects.filter(occupied = True, tenure = 'LT').values(
			'block__block_name').annotate(lt_occupied_beds=Count('bed')).order_by('block__block_name')
	st_blocks_occ = Occupancy_dashboard.objects.filter(occupied = True, tenure = 'ST').values(
			'block__block_name').annotate(st_occupied_beds=Count('bed')).order_by('block__block_name')
	blocks_blkd = Occupancy_dashboard.objects.filter(blocked = True).values(
			'block__block_name').annotate(blocked_beds=Count('bed')).order_by('block__block_name')
	
	total_beds = occupancy_dashboard.count()
	lt_occupied_beds = lt_occ_beds.count()
	st_occupied_beds = st_occ_beds.count()
	blocked_beds = blkd_beds.count()
	vacant_beds = total_beds - (lt_occupied_beds + st_occupied_beds)- blocked_beds
	percent = round((lt_occupied_beds + st_occupied_beds) / total_beds * 100)
	
	return render(request, 'guesthouse/room_occupancy_report.html', 
			{'occupancy_dashboard':occupancy_dashboard, 'blocks_total':blocks_total,
			'lt_blocks_occ':lt_blocks_occ, 'vacant_beds':vacant_beds, 'lt_occupied_beds':lt_occupied_beds,
			'percent':percent, 'total_beds':total_beds, 'blocked_beds':blocked_beds,
			'blocks_blkd':blocks_blkd, 'st_occupied_beds':st_occupied_beds, 
			'st_blocks_occ':st_blocks_occ,'blocks_occ':blocks_occ})
	
def get_bed_occupant_details(request):
	
	b_id = request.GET.get('bed_id', '')
	print(b_id)
	
	bed = room_alloc = Room_allocation.objects.filter( Q(bed_id = b_id) &
			(Q( allocation_end_date__gt = today, bed_id__isnull = False) |
			Q(allocation_end_date__isnull = True, bed_id__isnull = False))	
		).select_related('guest', 'booking', 'block','floor','room').first()
			
	return render(request, 'guesthouse/bed_occupant_details.html', {'bed':bed})

@login_required	
def guest_account_booking(request):
	return render(request, 'guesthouse/guest_account_booking.html', {} )


def guest_account_report(request, booking_number):

	booking = Booking.objects.get(booking_number = booking_number)
	room_alloc = Room_allocation.objects.filter(booking_id = booking_number).order_by('updated_date').last()

	# Receipts with bill
	rcts_with_bill = Receipt.objects.filter(booking_id = booking_number, bill_id__isnull = False)
	rcts_with_bill_ids = Receipt.objects.filter(booking_id = booking_number, bill_id__isnull = False).values_list('bill_id', flat=True)

	# Receipts without bill
	rcts_without_bill = Receipt.objects.filter(booking_id = booking_number, bill__isnull = True)
	
	# All Bills without receipts
	bills_without_receipts = Bill.objects.filter(booking_id = booking_number).exclude(bill_number__in = rcts_with_bill_ids)

	bills_sum = Bill.objects.filter(booking_id = booking_number).aggregate(bill_amt=Sum('amount'))
		
	rcts_sum = Receipt.objects.filter(booking_id = booking_number).exclude(
				receipt_for__in =['AD', 'BK']).aggregate(rct_amt=Sum('amount'))

	total_bill_amt = bills_sum['bill_amt']
	total_rct_amt = rcts_sum['rct_amt']
		
	# Result set is Transaction Date, Bill Amt, Rct amt, Type, For_month
	results = []
	for r in rcts_without_bill:
		row = {}
		row['id'] = r.receipt_number
		row['date'] = r.receipt_date
		row['bill_amt'] = None
		row['rct_amt'] = r.amount
		row['type'] = r.get_receipt_for_display
		row['For Month'] = r.receipt_for_month
		
		results.append(row)
	
	for rb in rcts_with_bill:
		row = {}
		row['id'] = rb.receipt_number
		row['date'] = rb.receipt_date
		row['bill_amt'] = rb.bill.amount
		row['rct_amt'] = rb.amount
		row['type'] = rb.get_receipt_for_display
		row['month'] = rb.receipt_for_month
		
		results.append(row)

	for b in bills_without_receipts:
		row = {}
		row['id'] = b.bill_number
		row['date'] = b.bill_date
		row['bill_amt'] = b.amount
		row['rct_amt'] = None
		row['type'] = b.get_bill_for_display
		row['month'] = b.bill_for_month
		
		results.append(row)
		
	result_set = sorted(results, key=lambda k: k['date'])	
	
	return render(request, 'guesthouse/guest_account_report.html', {'result_set':result_set, 
		'total_bill_amt':total_bill_amt, 'total_rct_amt':total_rct_amt, 'booking':booking,
		'room_alloc':room_alloc})

@login_required		
def bills_receipts_report(request):

	room_alloc = Room_allocation.objects.filter( Q(allocation_start_date__lte = today) &
		( Q(allocation_end_date__gte = today, bed_id__isnull = False) |	
		  Q(allocation_end_date__isnull = True, bed_id__isnull = False) )
		).order_by('allocation_start_date')
		
	result_set = []
	total_advance = 0
	total_unpaid_bills = 0
	total_bills = 0
	total_rcts = 0
	outstanding = 0
	total_expected_advance = 0
	total_expected_rent = 0
	
	
	# Remove earlier data
	Bills_receipts_dashboard.objects.all().delete()
	for r in room_alloc:
		row = {}

		# Expected Advance and Rent
		r_conv = Room_conversion.objects.filter(room_id = r.room_id, 
				available_from__lte = r.allocation_start_date).last()
		expected_adv = 0
		if r_conv :
			if r.booking.tenure == 'LT':
				expected_adv = r_conv.advance
			else: 
				expected_adv = r_conv.short_term.advance			
		else:
			if r.booking.tenure == 'LT':
				expected_adv = r.room.advance
			else:
				expected_adv = r.room.short_term_advance
			
		# advance receipt
		adv_rcts = Receipt.objects.filter(booking_id = r.booking_id, 
				receipt_for__in = ['AD', 'BK']).aggregate(adv_paid=Sum('amount'))
								
		# Rent bills and receipts		
		rent_bills = Bill.objects.filter(booking_id = r.booking_id,
				bill_for__in = ['RN','AR']).aggregate(rent_bill_amt=Sum('amount'))
		rent_rcts = Receipt.objects.filter(booking_id = r.booking_id,
				receipt_for__in =['RN', 'AR']).aggregate(rent_rct_amt=Sum('amount'))
			
		# Food bills and receipts		
		food_bills = Bill.objects.filter(booking_id = r.booking_id,
				bill_for = 'FD').aggregate(food_bill_amt=Sum('amount'))
		food_rcts = Receipt.objects.filter(booking_id = r.booking_id,
				receipt_for ='FD').aggregate(food_rct_amt=Sum('amount'))

		# Outstanding as of 31-Mar-2019		
		outstanding_bills = Bill.objects.filter(booking_id = r.booking_id,
				bill_for = 'OS').aggregate(os_bill_amt=Sum('amount'))
		os_rcts = Receipt.objects.filter(booking_id = r.booking_id,
				receipt_for ='OS').aggregate(os_rct_amt=Sum('amount'))

		bills_sum = Bill.objects.filter(booking_id = r.booking_id).aggregate(bill_amt=Sum('amount'))
			
		rcts_sum = Receipt.objects.filter(booking_id = r.booking_id).exclude(
				receipt_for__in =['AD', 'BK']).aggregate(rct_amt=Sum('amount'))
		
		all_bills = 0
		if bills_sum['bill_amt']:
			all_bills = bills_sum['bill_amt']
		
		all_rcts = 0
		if rcts_sum['rct_amt']:
			all_rcts = rcts_sum['rct_amt']
			
		outstanding_amt =  all_bills - all_rcts
				
		tab_row = Bills_receipts_dashboard(
			booking = r.booking,
			guest = r.guest,
			bed = r.bed,
			room = r.room,
			floor = r.floor,
			block = r.block,
			expected_advance = expected_adv,
			advance_rct = adv_rcts['adv_paid'],
			expected_rent = rent_bills['rent_bill_amt'],
			rent_rct = rent_rcts['rent_rct_amt'],
			expected_food_charges = food_bills['food_bill_amt'],
			food_charges_rct =  food_rcts['food_rct_amt'],
			outstanding_31Mar = outstanding_bills['os_bill_amt'],
			os_received = os_rcts['os_rct_amt'],
			outstanding_amont = outstanding_amt,
			created_date = today
		)
		tab_row.save()		
				
	## Report data
	dashboard = Bills_receipts_dashboard.objects.all().order_by('block')
	
	blocks = Bills_receipts_dashboard.objects.values('block__block_name').distinct().order_by('block__block_name')
	
	#tda = dashboard.aggregate(adv_due=Sum('expected_advance'))
	tda = dashboard.values('block__block_name').annotate(adv_due=Sum('expected_advance')).order_by('block')	
	total_due_adv = dashboard.values('block').aggregate(adv_due=Sum('expected_advance'))

	#taa = dashboard.aggregate(adv_rct=Sum('advance_rct'))
	taa = dashboard.values('block__block_name').annotate(adv_rct=Sum('advance_rct')).order_by('block')
	total_adv_amt = dashboard.aggregate(adv_rct=Sum('advance_rct'))

	#trd = dashboard.aggregate(rent_due=Sum('expected_rent'))
	trd = dashboard.values('block__block_name').annotate(rent_due=Sum('expected_rent')).order_by('block')
	total_rent_due = dashboard.aggregate(rent_due=Sum('expected_rent'))
	
	#tra = dashboard.aggregate(rent_rct=Sum('rent_rct'))
	tra = dashboard.values('block__block_name').annotate(rn_rct=Sum('rent_rct')).order_by('block')
	total_rent_amt = dashboard.aggregate(rn_rct=Sum('rent_rct'))
	tr = 0
	if total_rent_amt['rn_rct'] :
		tr = round(total_rent_amt['rn_rct'])
	
	#tfd = dashboard.aggregate(food_due=Sum('expected_food_charges'))
	tfd = dashboard.values('block__block_name').annotate(food_due=Sum('expected_food_charges')).order_by('block')
	total_food_due = dashboard.aggregate(food_due=Sum('expected_food_charges'))

	#tfa = dashboard.aggregate(rent_rct=Sum('food_charges_rct'))
	tfa = dashboard.values('block__block_name').annotate(food_rct=Sum('food_charges_rct')).order_by('block')
	total_food_amt = dashboard.aggregate(food_rct=Sum('food_charges_rct'))
	tf = 0
	if total_food_amt['food_rct']:
		tf = round(total_food_amt['food_rct'])
		
	#to3 = dashboard.aggregate(os_31mar=Sum('outstanding_31Mar'))
	to31 = dashboard.values('block__block_name').annotate(os_31mar=Sum('outstanding_31Mar')).order_by('block')
	total_outstanding_31Mar = dashboard.aggregate(os_31mar=Sum('outstanding_31Mar'))

	tor = dashboard.values('block__block_name').annotate(os_received=Sum('os_received')).order_by('block')
	total_os_amt = dashboard.aggregate(os_received=Sum('os_received'))
	to = 0
	if total_os_amt['os_received']:
		to = round(total_os_amt['os_received'])
	
	#toa = dashboard.aggregate(outstanding_amt=Sum('outstanding_amont'))
	toa = dashboard.values('block__block_name').annotate(outstanding_amt=Sum('outstanding_amont')).order_by('block')
	total_outstanding_amt = dashboard.aggregate(outstanding_amt=Sum('outstanding_amont'))
	
	r = 0
	if total_rent_due['rent_due']:
		r = round(total_rent_due['rent_due'])
	f = 0
	if total_food_due['food_due']:
		f = round(total_food_due['food_due'])
	t = 0
	if total_outstanding_31Mar['os_31mar']:
		t = round(total_outstanding_31Mar['os_31mar'])
	total_due = round(r + f + t)
	total_rcts = round(tr + tf + to)
	
	return render(request, 'guesthouse/bills_receipts_report.html', {'dashboard':dashboard, 
		'tda':tda, 'taa':taa, 'trd':trd, 'tra':tra, 'tfd':tfd, 'tfa':tfa, 'to31':to31, 'toa':toa,
		'total_due_adv':total_due_adv, 'total_adv_amt':total_adv_amt, 'total_rent_due':total_rent_due,
		'total_rent_amt':total_rent_amt, 'total_food_due':total_food_due, 'total_food_amt':total_food_amt,
		'total_outstanding_31Mar':total_outstanding_31Mar, 'total_outstanding_amt':total_outstanding_amt,
		'blocks':blocks, 'total_due':total_due, 'total_rcts':total_rcts, 'tor':tor,
		'total_os_amt':total_os_amt})		

@login_required
def booking_report(request):
	
	return render(request, 'guesthouse/bookings_report.html')

@csrf_exempt	
def booking_report_table(request):

	from_date = request.POST.get("start_date", '')
	if from_date != '' :
		startDt = datetime.datetime.strptime(from_date+ " 23:59:59", "%Y-%m-%d %H:%M:%S")
	to_date = request.POST.get("end_date", '')
	if to_date != '' :
		endDt = datetime.datetime.strptime(to_date+ " 23:59:59", "%Y-%m-%d %H:%M:%S")
	else:
		endDt = None

	if endDt:
		bookings = Room_allocation.objects.filter(
			allocation_start_date__gte = startDt,
			allocation_end_date__lte = endDt).select_related('guest', 'booking',
					'block', 'floor','room','bed').order_by('-booking_id')
	else:
		bookings = Room_allocation.objects.filter(
			allocation_start_date__gte = startDt).select_related('guest', 'booking',
					'block', 'floor','room','bed').order_by('-booking_id')
		
	count = bookings.count()

	return render(request, 'guesthouse/bookings_report_table.html', {'count':count, 
		'bookings': bookings, 'startDt':startDt, 'endDt':endDt})				
	

@login_required	
def waiting_list(request):

	room_alloc = Room_allocation.objects.values_list('booking_id', flat=True)
	bookings = Booking.objects.all().exclude( 
		booking_number__in = room_alloc).select_related(
			'guest').order_by('booking_number')
		
	count = bookings.count()

	return render(request, 'guesthouse/waiting_list.html', {'bookings':bookings,
		'count':count})				

@login_required
def monthly_due_bills_report(request):
	return render(request, 'guesthouse/monthly_due_bills_report.html', {})	

@login_required	
def monthly_due_bills_table(request):
	month = request.GET.get('month', '')
	rcts = Receipt.objects.filter(receipt_for_month = month, 
		bill_id__isnull = False).values_list('bill_id', flat=True)
	
	# Get unpaid bills 
	bills = Bill.objects.filter(bill_for_month = month, amount__gt = 0).exclude(
		bill_number__in = rcts)
	
	results = []
	for b in bills:
		rec = {}
		booking = b.booking
		room = Room_allocation.objects.filter(booking = booking).last()
		
		rec['bill_number'] = b.bill_number
		rec['booking_id'] = b.booking_id
		rec['first_name'] = b.guest.first_name
		rec['middle_name'] = b.guest.middle_name
		rec['last_name'] = b.guest.last_name
		if room:
			rec['room'] = room.block.block_name + "/" + room.floor.floor_name + "/" + room.room.room_name + "/" + room.bed.bed_name
		else: 
			rec['room'] = 'No Allocation'
		rec['phone_number'] = b.guest.phone_number
		rec['email_id'] = b.guest.email_id
		rec['bill_date'] = b.bill_date
		rec['amount'] = b.amount
		rec['get_bill_for_display'] = b.get_bill_for_display
		
		results.append(rec)
		
	
	return render(request, 'guesthouse/monthly_due_bills_table.html', {
		'bills':results, 'month':month})