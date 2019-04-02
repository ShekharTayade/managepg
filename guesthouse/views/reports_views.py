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

from django.http import JsonResponse

from .views import *
from guesthouse.models import Guesthouse, Booking, Guest, Room_allocation, Bill
from guesthouse.models import Receipt, Food_price, Vacation_period, Block, Floor
from guesthouse.models import Generate_number_by_month, Billing_error
from guesthouse.models import Room_conversion, Bed_conversion, Room, Bed, Occupancy_dashboard

today = datetime.datetime.today()


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
	
def room_occupancy_report(request):

	total_beds = Bed.objects.filter(available_from__lte = today,
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
			beds = total_beds.filter(room_id = tr.room_id)
		
		for b in beds:
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
				blocked = blocked,
				created_date = today
			)
			dashboard.save()
	
	occupancy_dashboard = Occupancy_dashboard.objects.all().order_by('block','floor','room', 'bed')
	occ_beds = Occupancy_dashboard.objects.filter(occupied = True).order_by('block','floor','room', 'bed')
	blkd_beds = Occupancy_dashboard.objects.filter(blocked = True).order_by('block','floor','room', 'bed')
	
	blocks_total = Occupancy_dashboard.objects.values(
			'block__block_name').annotate(total_beds=Count('bed')).order_by('block__block_name') 
	blocks_occ = Occupancy_dashboard.objects.filter(occupied = True).values(
			'block__block_name').annotate(occupied_beds=Count('bed')).order_by('block__block_name')
	blocks_blkd = Occupancy_dashboard.objects.filter(blocked = True).values(
			'block__block_name').annotate(blocked_beds=Count('bed')).order_by('block__block_name')

	
	total_beds = occupancy_dashboard.count()
	occupied_beds = occ_beds.count()
	blocked_beds = blkd_beds.count()
	vacant_beds = total_beds - occupied_beds - blocked_beds
	percent = round(occupied_beds / total_beds * 100)
	
	return render(request, 'guesthouse/room_occupancy_report.html', 
			{'occupancy_dashboard':occupancy_dashboard, 'blocks_total':blocks_total,
			'blocks_occ':blocks_occ, 'vacant_beds':vacant_beds, 'occupied_beds':occupied_beds,
			'percent':percent, 'total_beds':total_beds, 'blocked_beds':blocked_beds,
			'blocks_blkd':blocks_blkd})	
	
def get_bed_occupant_details(request):
	
	b_id = request.GET.get('bed_id', '')
	print(b_id)
	
	bed = room_alloc = Room_allocation.objects.filter( Q(bed_id = b_id) &
			(Q( allocation_end_date__gt = today, bed_id__isnull = False) |
			Q(allocation_end_date__isnull = True, bed_id__isnull = False))	
		).select_related('guest', 'booking', 'block','floor','room').first()
			
	return render(request, 'guesthouse/bed_occupant_details.html', {'bed':bed})


		
	
	