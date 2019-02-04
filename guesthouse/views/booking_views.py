from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count
from django.conf import settings

from datetime import datetime
import datetime
import json

from .views import *
from guesthouse.forms import BookingForm, GuestForm, Room_allocationForm
from guesthouse.models import Guesthouse, Booking, Guest, Room_allocation, Generate_number_by_month

today = datetime.date.today()
def booking_form_new(request):

 
	if request.method == 'POST':

		#booking = Booking.objects.get(booking_number = form.booking_number)	
		
		# Parse request into the three forms
		guest_form = GuestForm(request.POST.copy(), request.FILES, prefix = "guest")
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
								validation_msg.append("Please allocated Room/Bed.")
							
							
							room_allocation_form = Room_allocationForm(request.POST.copy(), instance = room, prefix="room")
							room_allocation_form.data['room-alloc_id'] = room.alloc_id
							room_allocation_form.data['room-booking'] = room.booking
							room_allocation_form.data['room-guest'] = room.guest
							
	else:
		booking_form = BookingForm(prefix="booking",)

		guest_form = GuestForm(prefix="guest",
				initial={'current_state': 'KARNATAKA', 'permanent_state':'KARNATAKA',
				'company_state':'KARNATAKA'})
		room_allocation_form = Room_allocationForm(prefix="room",)
		validation_msg = []

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
		
	
	return render(request, 'guesthouse/booking_widget_tweaks.html', {
		'booking_form': booking_form, 'guest_form':guest_form, 'room_allocation_form':room_allocation_form,
		'country_arr':country_arr, 'state_arr':state_arr, 'city_arr':city_arr, 'pin_code_arr':pin_code_arr, 
		'validation_msg':validation_msg
		})



def booking_form(request):

 
	if request.method == 'POST':
		
		# Parse request in to the three forms
		g_form = parseToForm("guest_form.",request.POST, request.FILES)
		b_form = parseToForm("booking_form.",request.POST, request.FILES)
		r_form = parseToForm("room_allocation_form.",request.POST, request.FILES)

		guest_form = GuestForm(g_form)

		# Get DB values as required
		guest_form = set_DB_values_for_fields("guest_form", guest_form)
		
		booking_form = BookingForm(b_form)
		# Get DB values as required
		booking_form = set_DB_values_for_fields("booking_form", booking_form)

		room_allocation_form = Room_allocationForm(r_form)
		# Get DB values as required
		room_allocation_form = set_DB_values_for_fields("room_allocation_form", booking_form)

		
		validations = applyBookingValidations(guest_form, booking_form, room_allocation_form)
		validation_result = validations['result']
		validation_msg = validations['msg']
		
		if validation_result:
			if guest_form.is_valid():
				guest = guest_form.save(commit=False)
				guest.save()

				if booking_form.is_valid():
					booking = booking_form.save(commit=False)
					booking.guest_id = guest.guest_id
					booking.guesthouse_id = settings.GH_ID
					booking.booking_number = getNextbookingNumber()
					booking.save()
					# Create, Update room allocation, only if check_in_date is present
					if room_allocation_form.data['check_in_date'] :
						if room_allocation_form.is_valid():
							room_allocation_form.data['booking_id'] = booking.booking_id
							room_allocation_form.data['guest_id'] = booking.guest_id
							room = room_allocation_form.save(commit=False)
							room.save()
				
							validation_msg.append("New booking is saved.")
				
	else:
		#booking_form = BookingForm()
		#guest_form = GuestForm(initial={'current_state': 'KARNATAKA'})
		#room_allocation_form = Room_allocationForm()
		guest_form = {}
		booking_form = {}
		room_allocation_form = {}
		
		validations = applyBookingValidations(guest_form, booking_form, room_allocation_form)
		validation_result = validations['result']
		validation_msg = validations['msg']
		
		guest_form = GuestForm(initial={'current_state': 'KARNATAKA'})
		booking_form = BookingForm()
		room_allocation_form = Room_allocationForm()
	# set initial values
	init_values = set_initial_values( guest_form, booking_form )

	
	
	return render(request, 'guesthouse/booking_widget_tweaks.html', {
		'booking_form': booking_form, 'guest_form':guest_form, 'room_allocation_form':room_allocation_form,
		'country_arr':init_values['country_arr'], 'state_arr':init_values['state_arr'],
		'city_arr':init_values['city_arr'], 'pin_code_arr':init_values['pin_code_arr'], 
		'validation_msg':validation_msg,
		'occup_list':init_values['occup_list'], 'occupation':init_values['occupation'], 
		'gender':init_values['gender'], 'food_option':init_values['food_option'], 
		'food_preference': init_values['food_preference'], 
		'food_pref_list':init_values['food_pref_list'], 'tenure':init_values['tenure'] 
		})


def set_initial_values(guest_form, booking_form):
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

		
	food_pref_list = ["Vegetarian", "Non-Vegetarian"]
	occup_list = ["Studying", "Working"] # Default value for Occupation
	gender = "Female"
		
	if guest_form.data :
		if guest_form.data['occupation'] == "ST":
			occupation = "Studying"
		else:
			occupation = "Working"
	else :
		occupation = "Studying"
	
			
		
	if booking_form.data :
		# Set values from the current forms
		if booking_form.data['food_option'] :
			food_option = "Yes"
		else :
			food_option = "No"
			
		if booking_form.data['food_preference'] == "VEG":
			food_preference = "Vegetarian"
		else :
			food_preference = "Vegetarian"
		if booking_form.data['tenure'] == "ST":
			tenure = "One Month"
		else:
			tenure = "Long Term"
	else:
		food_preference = "Vegetarian"
		tenure = "Long Term"
		food_option = "Yes"
		
	return {'country_arr':country_arr, 'state_arr':state_arr,
		'city_arr':city_arr, 'pin_code_arr':pin_code_arr, 'occupation':occupation, 'occup_list':occup_list, 
		'gender':gender, 'food_option': food_option,'food_pref_list':food_pref_list, 
		'food_preference':food_preference, 'tenure':tenure}

def set_DB_values_for_fields( form_name, form ):

	if form_name == "guest_form":
		if form.data['occupation'] == "Studying":
			form.data['occupation'] = "ST"
		if form.data['occupation'] == "Working":
			form.data['occupation'] = "SR"
		if form.data['gender'] == "Female":
			form.data['gender'] = "FEMALE"
		if form.data['gender'] == "Male":
			form.data['gender'] = "MALE"
		
		if form.data['parent_guardian_1_type'] == "Father":
			form.data['parent_guardian_1_type'] = "FATHER"
		if form.data['parent_guardian_1_type'] == "Mother":
			form.data['parent_guardian_1_type'] = "MOTHER"
		if form.data['parent_guardian_1_type'] == "Husband":
			form.data['parent_guardian_1_type'] = "HUSBAND"
		if form.data['parent_guardian_1_type'] == "Wife":
			form.data['parent_guardian_1_type'] = "Wife"
		if form.data['parent_guardian_1_type'] == "Guardian":
			form.data['parent_guardian_1_type'] = "GUARDIAN"

		if form.data['parent_guardian_2_type'] == "Father":
			form.data['parent_guardian_2_type'] = "FATHER"
		if form.data['parent_guardian_2_type'] == "Mother":
			form.data['parent_guardian_2_type'] = "MOTHER"
		if form.data['parent_guardian_2_type'] == "Husband":
			form.data['parent_guardian_2_type'] = "HUSBAND"
		if form.data['parent_guardian_2_type'] == "Wife":
			form.data['parent_guardian_2_type'] = "Wife"
		if form.data['parent_guardian_2_type'] == "Guardian":
			form.data['parent_guardian_2_type'] = "GUARDIAN"
			
		if form.data['parent_guardian_3_type'] == "Father":
			form.data['parent_guardian_3_type'] = "FATHER"
		if form.data['parent_guardian_3_type'] == "Mother":
			form.data['parent_guardian_3_type'] = "MOTHER"
		if form.data['parent_guardian_3_type'] == "Husband":
			form.data['parent_guardian_3_type'] = "HUSBAND"
		if form.data['parent_guardian_3_type'] == "Wife":
			form.data['parent_guardian_3_type'] = "Wife"
		if form.data['parent_guardian_3_type'] == "Guardian":
			form.data['parent_guardian_3_type'] = "GUARDIAN"

	
	if form_name == "booking_form":
		if form.data['food_preference'] == "Vegetarian":
			form.data['food_preference'] = "VEG"
		if form.data['food_preference'] == "Non-Vegetarian":
			form.data['food_preference'] = "NON-VEG"
		
		if form.data['tenure'] == "One Month":
			form.data['tenure'] = "ST"
		if form.data['tenure'] == "Long Term":
			form.data['tenure'] = "LT"
			

	return form
		
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
	return {'result':result, 'msg':msg}
	
def get_room_availablity():

	rooms = {}
	return { 'rooms':rooms }
	