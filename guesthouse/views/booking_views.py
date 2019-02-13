from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count, Q
from django.conf import settings

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta

import datetime
import json

from .views import *
from guesthouse.forms import BookingForm, GuestForm, Room_allocationForm
from guesthouse.models import Guesthouse, Booking, Guest, Room_allocation 
from guesthouse.models import Generate_number_by_month, Bed, Room, Floor, Block

today = datetime.date.today()
def new_booking(request):

	validation_msg = []
	if request.method == 'POST':

		#booking = Booking.objects.get(booking_number = form.booking_number)	
		
		# Parse request into the three forms
		guest_form = GuestForm(request.POST.copy(), request.FILES, prefix = "guest")
		guest = {}
		booking_form = BookingForm(request.POST.copy(), prefix="booking")
		room_allocation_form = Room_allocationForm(request.POST.copy(), prefix="room")
		
		validations = applyBookingValidations(guest_form, booking_form, room_allocation_form)
		validation_result = validations['result']
		validation_msg = validations['msg']

		if validation_result:
			if guest_form.is_valid():
				guest = guest_form.save(commit=False)
				if guest_form.data['guest-guest_id'] != '':
					# Get instance alread in the DB
					g_inst = Guest.objects.get(guest_id = int(guest_form.data['guest-guest_id']))
					guest.guest_id = g_inst.guest_id
					guest.created_date = g_inst.created_date
				
				try :
					pin = guest_form.data['guest-current_pin_code']
					pinObj = Pin_code.objects.get( pin_code = pin )
					guest.current_pin_code = pinObj

					pin = guest_form.data['guest-permanent_pin_code']
					pinObj = Pin_code.objects.get( pin_code = pin )
					guest.permanent_pin_code = pinObj

					pin = guest_form.data['guest-company_pin_code']
					pinObj = Pin_code.objects.get( pin_code = pin )
					guest.company_pin_code = pinObj
				except Pin_code.DoesNotExist:
					None
				
				guest.save()
				validation_msg.append("Guest Details are saved.")

				guest_form = GuestForm(request.POST.copy(), instance = guest, prefix="guest")
				guest_form.data['guest-guest_id'] = guest.guest_id				
				
				if booking_form.is_valid():
					booking = booking_form.save(commit=False)
					
					booking.guest_id = guest.guest_id
					booking.guesthouse_id = settings.GH_ID

					if not booking_form.data['booking-booking_number'] or booking_form.data['booking-booking_number'] == '':
						booking.booking_number = getNextbookingNumber()
					else :
						b_obj = Booking.objects.get(booking_number = booking_form.data['booking-booking_number'] )
						booking.booking_number = booking_form.data['booking-booking_number']
						booking.created_date = b_obj.created_date

					booking.save()
					
					validation_msg.append("Booking is saved.")
					booking_form = BookingForm(request.POST.copy(), instance = booking, prefix="booking")
					booking_form.data['booking-booking_number'] = booking.booking_number
					booking_form.data['booking-guest'] = booking.guest
					booking_form.data['booking-guesthouse'] = booking.guesthouse
					
					# Create, Update room allocation, only if check_in_date is present
					if booking.check_in_date is not None:
						if room_allocation_form.is_valid():
							room = room_allocation_form.save(commit=False)
							if booking_form.data['room-alloc_id'] and booking_form.data['room-alloc_id'] != '':
								r_obj = Room_allocation.objects.get(alloc_id = booking_form.data['room-alloc_id'] )
								room.alloc_id = r_obj.alloc_id
								room.created_date = r_obj.created_date
							room.booking_id = booking.booking_number
							room.guest = booking.guest
							room.allocation_start_date = booking.check_in_date
							room.allocation_end_date = booking.check_out_date
							
							room.save()
							
							if room.bed :
								validation_msg.append("Room/Bed allocation is done.")
							else:
								validation_msg.append("Please allocate Room/Bed.")
							
							
							room_allocation_form = Room_allocationForm(request.POST.copy(), instance = room, prefix="room")
							room_allocation_form.data['room-alloc_id'] = room.alloc_id
							room_allocation_form.data['room-booking'] = room.booking
							room_allocation_form.data['room-guest'] = room.guest
							
	else:

		booking_form = BookingForm(prefix="booking",)

		guest_form = GuestForm(prefix="guest",
				initial={'current_state': 'KARNATAKA', 'permanent_state':'KARNATAKA',
				'company_state':'KARNATAKA'})
		guest = {} # passing an empty guest instance, it's used in POST to dsiplay the photo in the browser
		room_allocation_form = Room_allocationForm(prefix="room")
	
	# Get available beds, and pass to front end
	room_availability = get_availablity(request, today)
	blocks = room_availability['blocks']
	floors = room_availability['floors']
	rooms = room_availability['rooms']
	beds = room_availability['beds']

	if beds is None:
		validation_msg.append['There is no availability currently!!']

	country_list = Country.objects.all()
	country_arr = []
	for c in country_list:
		country_arr.append(c.country_name)
		
	state_list = State.objects.all()
	state_arr = []
	for s in state_list:
		state_arr.append(s.state_name)
		

	city_list = City.objects.all()
	city_arr = []
	for ct in city_list:
		city_arr.append(ct.city)

	pin_code_list = Pin_code.objects.all()
	pin_code_arr = []
	for p in pin_code_list:
		pin_code_arr.append(p.pin_code)		
		
	print(beds)
	return render(request, 'guesthouse/new_booking.html', {
		'booking_form': booking_form, 'guest_form':guest_form, 'room_allocation_form':room_allocation_form,
		'country_arr':country_arr, 'state_arr':state_arr, 'city_arr':city_arr, 'pin_code_arr':pin_code_arr, 
		'validation_msg':validation_msg, 'guest':guest, 'beds':beds, 'rooms':rooms, 
		'floors':floors, 'blocks':blocks
		})

	
def parseToForm(form_str, data, files):

	form = {}

	# all names starting with form_str belong to the form
	for field, value in data.items():
		
		if field.startswith(form_str):
			form[field.replace(form_str, '')] = value

	return form
			
def getNextbookingNumber():
	booking_num = 0
	#Get curentyear, month in format YYYYMM
	dt = datetime.datetime.now()
	mnth = dt.strftime("%Y%m")

	# Get an suffix required 
	guesthouse = Guesthouse.objects.get(gh_id = settings.GH_ID)
	suffix = guesthouse.month_year_suffix
	
	monthyear = Generate_number_by_month.objects.filter(type='BOOKING-NUMBER', month_year = mnth).first()
	if monthyear :
		booking_num = monthyear.current_number + 1
	else :
		booking_num = 1
		
	# Update generated number in DB
	num = Generate_number_by_month(
		type = 'BOOKING-NUMBER',
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

	
def applyBookingValidations(guest_form, booking_form, room_allocation_form):

	result = True
	msg = []

	
	if guest_form:
		validation = validate_address(guest_form.data['guest-current_pin_code'],
				guest_form.data['guest-current_city'],
				guest_form.data['guest-current_state'],
				guest_form.data['guest-current_country'])
		if not validation['valid']:
			msg.append( validation['msg'])
			result = False

	if booking_form:
		if booking_form.data['booking-check_in_date'] != '' and  booking_form.data['booking-check_out_date'] != '' :
			check_in = datetime.datetime.strptime( booking_form.data['booking-check_in_date'], '%Y-%m-%d' )
			check_out = datetime.datetime.strptime( booking_form.data['booking-check_out_date'], '%Y-%m-%d')
			if check_out <= check_in:
				msg.append("Room Allocation -> Check-out should be later than check-in")
				result = False
			
			import pdb
			pdb.set_trace()
			
			diff = (check_out.year - check_in.year) * 12 + check_out.month - check_in.month
			if booking_form.data['booking-tenure'] == 'LT':
				if diff < 12:
					msg.append("Room Allocation -> Long Term stay can't be less than 1 year")
					result = False
					
			if booking_form.data['booking-tenure'] == 'ST':
				if diff > 1:
					msg.append("Room Allocation -> Short Term stay can't be more than 1 month")
					result = False
		
		
	return {'result':result, 'msg':msg}
	
def get_availablity(request, from_date):

	# Get all beds currently allocated
	bed_alloc = Room_allocation.objects.filter(
		allocation_end_date__gt = from_date, bed_id__isnull = False).values('bed_id')

	# Get the currently available beds (exclude allocated beds)
	beds = Bed.objects.exclude(bed_id__in=bed_alloc)

	rooms_arr = []
	floors_arr = [] 
	blocks_arr = []
	for b in beds:
		if b.room not in rooms_arr:
			rooms_arr.append(b.room_id)
		if b.floor not in rooms_arr:
			floors_arr.append(b.floor_id)
		if b.block not in rooms_arr:
			blocks_arr.append(b.block_id)
	
	rooms = Room.objects.filter(room_id__in = rooms_arr)
	floors = Floor.objects.filter(floor_id__in = floors_arr)
	blocks = Block.objects.filter(block_id__in = blocks_arr)
	
	return { 'beds':beds, 'rooms':rooms, 'floors':floors, 'blocks':blocks }

def manage_booking(request):
	
	return render(request, 'guesthouse/manage_booking.html', {} )

@csrf_exempt
def get_bookings(request):
	
	from_date = request.POST.get("fromdate", '')
	startDt = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()	
	to_date = request.POST.get("todate", '')
	endDt = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()	

	bookings_list = Booking.objects.all().select_related('guest')
	
	if startDt:
		bookings_list = bookings_list.filter(created_date__gte = startDt)
		
	if endDt:
		bookings_list = bookings_list.filter(created_date__lte = endDt)
	
	count = bookings_list.count()

	page = request.GET.get('page', 1)

	paginator = Paginator(bookings_list, 5)
	try:
		bookings = paginator.page(page)
	except PageNotAnInteger:
		bookings = paginator.page(1)
	except EmptyPage:
		bookings = paginator.page(paginator.num_pages)
	
	return render(request, 'guesthouse/bookings_table.html', {'count':count, 
		'bookings': bookings})		
	
	