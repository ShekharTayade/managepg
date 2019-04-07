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
		
	rcts_sum = Receipt.objects.filter(booking_id = booking_number).aggregate(rct_amt=Sum('amount'))

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
	for r in room_alloc:
		row = {}
		
		# Bills without receipts
		rcts_with_bill_ids = Receipt.objects.filter(booking_id = r.booking_id, bill_id__isnull = False).values_list('bill_id', flat=True)
		unpaid_bills = Bill.objects.filter(booking_id = r.booking_id).exclude(
				bill_number__in = rcts_with_bill_ids).aggregate(unpaid_bill_amt=Sum('amount'))
		
		rcts = Receipt.objects.filter(booking_id = r.booking_id, 
				receipt_for__in = ['AD', 'BK']).aggregate(adv_sum=Sum('amount'))

		bills_sum = Bill.objects.filter(booking_id = r.booking_id).aggregate(bill_amt=Sum('amount'))
			
		rcts_sum = Receipt.objects.filter(booking_id = r.booking_id).aggregate(rct_amt=Sum('amount'))
				
		row['booking_number'] = r.booking_id
		row['guest_name'] = r.guest.first_name + ' ' + r.guest.middle_name + ' ' + r.guest.last_name
		row['advance'] = rcts['adv_sum']
		row['unpaid_bill_amt'] = unpaid_bills['unpaid_bill_amt']
		row['total_bills'] = bills_sum['bill_amt']
		row['total_receipts'] = rcts_sum['rct_amt']

		
		if bills_sum['bill_amt']:
			bill_amt = bills_sum['bill_amt']
		else:
			bill_amt = 0
		if rcts_sum['rct_amt']:
			rct_amt = rcts_sum['rct_amt']
		else:
			rct_amt = 0
		if rcts['adv_sum']:
			adv_amt = rcts['adv_sum']
		else:
			adv_amt = 0
		if unpaid_bills['unpaid_bill_amt']:
			unpaid_bill_amt = unpaid_bills['unpaid_bill_amt']
		else:
			unpaid_bill_amt = 0
			
		row['outstanding'] = bill_amt - ( rct_amt - adv_amt )

		total_advance = total_advance + adv_amt
		total_unpaid_bills = total_unpaid_bills + unpaid_bill_amt
		total_bills = total_bills + bill_amt
		total_rcts = total_rcts + rct_amt
		outstanding = total_bills - total_rcts - total_advance
		result_set.append(row)

	return render(request, 'guesthouse/bills_receipts_report.html', {'result_set':result_set, 
		'total_bills':total_bills, 'total_rcts':total_rcts, 'total_advance':total_advance,
		'total_unpaid_bills':total_unpaid_bills, 'outstanding':outstanding})		
	