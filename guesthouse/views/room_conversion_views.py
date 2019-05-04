from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count, Q, Max, Min
from django.contrib.auth.decorators import login_required

from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta

from django.http import JsonResponse

from .views import *
from guesthouse.forms import RoomForm, Room_convForm
from guesthouse.models import Guesthouse, Booking, Guest, Room_allocation 
from guesthouse.models import Bed, Room, Floor, Block
from guesthouse.models import Room_conversion, Bed_conversion
from guesthouse.decorators import user_is_manager

today = datetime.date.today()

@login_required
@user_is_manager
def room_conversion(request):
	
	blocks = Block.objects.all()
	
	
	return render(request, "guesthouse/room_conversion.html", {'blocks':blocks})

@csrf_exempt
@user_is_manager
def room_form(request):
	room_id = request.GET.get("room_id", "")
	room = Room.objects.get(room_id = room_id)
	roomForm = RoomForm(instance=room)

	# Check for room conversion
	room_conv = Room_conversion.objects.filter(room_id = room_id, available_from__lte = today,
		available_to__gte = today)
	conv_flag = False
	if room_conv:
		conv_flag = True
	
	return render(request, "guesthouse/room_Form.html", {'form':roomForm, 
		'conv_flag': conv_flag, 'room_id':room_id})
	
@csrf_exempt
@user_is_manager
def room_conv_form(request):
	
	room_id = request.GET.get("room_id", "")
	try:
		room = Room_conversion.objects.get(room_id = room_id)
		room_convForm = Room_convForm(instance=room)
	except Room_conversion.DoesNotExist:
		room_convForm = {}		
		
	return render(request, "guesthouse/room_convForm.html", {'room_convForm':room_convForm, 'room_id':room_id})
	
@csrf_exempt	
def get_floors_by_block(request):
	block_id = request.POST.get('block_id','')
	
	floors = {}
		
	# Get the currently available floors (by excluding allocated beds)
	floors = Floor.objects.filter(block_id = block_id).order_by('floor_name').values(
		'floor_id', 'floor_name')
			
	return JsonResponse({'floors':list(floors)}, safe=False)
	
	
@csrf_exempt
def get_rooms_by_floor(request):
	floor_id = request.POST.get('floor_id','')
	rooms = Room.objects.filter(floor_id = floor_id).order_by('room_name').values(
		'room_id', 'room_name')
		
	return JsonResponse({'rooms':list(rooms)})

@csrf_exempt
def get_room_details(request):
	room_id = request.POST.get('room_id','')
	room = Room.objects.filter(room_id = room_id).values('room_id', 'room_name',
			'floor_id', 'block_id', 'available_from', 'available_to', 'rent_per_bed',
			'max_beds', 'advance', 'short_term_rent_per_bed')

	return JsonResponse({'room':list(room)})	
	
@csrf_exempt
def get_beds_by_room(request):
	room_id = request.POST.get('room_id','')
	beds = Bed.objects.filter(room_id = room_id).order_by('bed_name'). values(
		'bed_id', 'bed_name', 'available_from', 'available_to')
	
	return JsonResponse({'beds':list(beds)})

@csrf_exempt
def get_room_conversion(request):
	room_id = request.POST.get('room_id','')

	room_conv = Room_conversion.objects.filter(room_id = room_id,
		available_from__lte = today, available_to__gte = today)
		
	bed_conv = Bed_conversion.objects.filter(room_id = room_id,
		available_from__lte = today, available_to__gte = today)
		
	return JsonResponse({'room_conv':list(room_conv), 'bed_conv':list(bed_conv)})

@login_required	
@user_is_manager
def convert_room(request, room_id):
	room = {}
	room_convForm = {}
	beds = {}
	err_flag = False
	err_msg = ''
	
	if room_id != '':
		room = Room.objects.get(room_id = room_id)

		conv_flag = False
		# Check for room conversion
		room_conv = Room_conversion.objects.filter(room_id = room_id, available_from__lte = today,
			available_to__gte = today)
		if room_conv:
			conv_flag = True
		
		room_convForm = Room_convForm(instance=room)
		
		beds = Bed.objects.filter(room_id = room_id)
	
	if request.method =='POST':
		
		room_id = request.POST.get("room_id", "")
		room_convForm = Room_convForm(request.POST, instance=room)
		fm_dt = datetime.datetime.strptime(room_convForm.data['available_from'], '%Y-%m-%d' )
		to_dt = datetime.datetime.strptime(room_convForm.data['available_to'], '%Y-%m-%d' )
		beds_cnt = int(room_convForm.data['max_beds'])
		block = int(room_convForm.data['block'])
		floor = int(room_convForm.data['floor'])

		room_name = room_convForm.data['room_name']
		rent_per_bed = room_convForm.data['rent_per_bed']
		max_beds = beds_cnt
		advance = room_convForm.data['advance']
		short_term_rent_per_bed = room_convForm.data['short_term_rent_per_bed']

		if to_dt < fm_dt:
			err_flag = True
			err_msg = "Room available to date can't be earlier than available from date"		
		
		# Check that Bed availablity dates are within the Room availability date
		for b in range(beds_cnt):
			f = 'date_from_' + str( b+1 )
			b_fm = datetime.datetime.strptime(room_convForm.data[f], '%Y-%m-%d' )	
			t = 'date_to_' + str( b+1 )
			b_to = datetime.datetime.strptime(room_convForm.data[t], '%Y-%m-%d' )
			bd = 'bed_' + str(b+1)
			bed_name = room_convForm.data[bd]
					
			if (b_fm > to_dt) or (b_fm < fm_dt):				
				err_flag = True
				err_msg = "Bed " + bed_name + ": available from and to dates should be within room available from and to dates. Please re-enter."
			if (b_to < fm_dt) or( b_to > to_dt):
				err_flag = True
				err_msg = "Bed " + bed_name + ": available from and to dates should be within room available from and to dates. Please re-enter."
			
			
		if not err_flag:
			
			try:
				room_c = Room_conversion(
					room_id = room_id,
					room_name = room_name,
					floor_id = floor,
					block_id = block,
					available_from = fm_dt,
					available_to = to_dt,
					rent_per_bed = rent_per_bed,
					max_beds = max_beds,
					advance = advance,
					short_term_rent_per_bed = short_term_rent_per_bed 
				)
				room_c.save()
					
			
				for b in range(beds_cnt):
					bd = 'bed_' + str(b+1)
					bed_name = room_convForm.data[bd]
					
					f = 'date_from_' + str(b+1)
					fm = room_convForm.data[f]
					
					t = 'date_to_' + str(b+1)
					to = room_convForm.data[t]
					bed = Bed_conversion (
						bed_name = bed_name,
						room_id = room_id,
						floor_id = floor,
						block_id = block,
						available_from = fm,
						available_to = to
					)
					bed.save()
					
				return redirect('room_conversion_confirmation', room_id=room_id)

			except Exception as error:
				err_flag = True
				err_msg = "System Error while converting the room. Please contact support team"
		else:
			room_convForm = Room_convForm(instance=room)
					
	return render(request, "guesthouse/convert_room.html", {'room':room, 'form':room_convForm,
		'bed':beds, 'err_flag': err_flag, 'err_msg':err_msg })

@login_required
@user_is_manager
def room_conversion_confirmation(request, room_id):

	room_conv = {}
	try:
		room_conv = Room_conversion.objects.get(room_id = room_id)
	except Room_conversion.DoesNotExist:
		None
		
	bed_conv = Bed_conversion.objects.filter(room_id = room_id)
	
	return render(request, "guesthouse/room_conversion_confirmation.html", {'room_conv':room_conv,
		'bed_conv':bed_conv})

@csrf_exempt		
def cancel_conversion(request):

	status = "SUCCESS"
	room_conv = {}
	
	room_id = request.POST.get("room_id","")
	
	try:
		room_conv = Room_conversion.objects.get(room_id = room_id)
	except Room_conversion.DoesNotExist:
		status = "NOT-FOUND"
		
	bed_conv = Bed_conversion.objects.filter(room_id = room_id).delete()	
	room_conv.delete()

	return JsonResponse({'status':status})	

@login_required
@user_is_manager	
def manage_room(request):
	
	blocks = Block.objects.all()
	
	return render(request, "guesthouse/rooms.html", {'blocks':blocks})
	
@login_required
@user_is_manager
def room_detailsForm(request):	

	room_id = request.GET.get("room_id", "")
	room = Room.objects.get(room_id = room_id)
	# Check for room conversion
	room_conv = Room_conversion.objects.filter(room_id = room_id, available_from__lte = today,
		available_to__gte = today).last()
	conv_flag = False
	if room_conv:
		conv_flag = True
		form = Room_convForm(instance=room_conv)
	else:
			form = RoomForm(instance=room)
	
	return render(request, "guesthouse/room_detailsForm.html", {'form':form, 
		'conv_flag': conv_flag, 'room_id':room_id})

@login_required
@user_is_manager		
def room_modify(request):
	err_flag = False
	msg = ''
	if request.method == "POST":
		room_id = request.POST.get("room_id", "")

		room = Room.objects.filter(room_id = room_id, available_from__lte = today,
			available_to__gte = today).last()
		room_conv = Room_conversion.objects.filter(room_id = room_id, available_from__lte = today,
			available_to__gte = today).last()
		flg = request.POST.get("conv_flag", "")
		if flg == '' or flg.upper() == 'FALSE':
			conv_flag = False
			form = RoomForm(request.POST.copy() or None, instance=room)
			beds = Bed.objects.filter(room_id = room_id).order_by('bed_name')
		if flg.upper() == 'TRUE':
			conv_flag = True
			form = Room_convForm(request.POST.copy() or None, instance=room_conv)
			beds = Bed_conversion.objects.filter(room_id = room_id).order_by('bed_name')
		
		results = validate_room_details(room_id, form, conv_flag)

		err_flag = results['err_flag']
		msg = results['err_msg']
		
		if form.is_valid():
			if not err_flag:
				room = form.save(commit=False)
				room.save()
				msg = "Changes are saved"

		form.data['available_from'] = room.available_from
		form.data['available_to'] = room.available_to
		form.data['rates_effective_from'] = room.rates_effective_from
		form.data['rates_effective_to'] = room.rates_effective_to
	else:
		room_id = request.GET.get("rooms", "")
		room = Room.objects.get(room_id = room_id)
		# Check for room conversion
		room_conv = Room_conversion.objects.filter(room_id = room_id, available_from__lte = today,
			available_to__gte = today).last()
		conv_flag = False
		if room_conv:
			conv_flag = True
			form = Room_convForm(instance=room_conv)
			beds = Bed_conversion.objects.filter(room_id = room_id).order_by('bed_name')
		else:
			form = RoomForm(instance=room)
			beds = Bed.objects.filter(room_id = room_id).order_by('bed_name')

	return render(request, "guesthouse/room_modify_confirm.html", {'form':form, 
		'conv_flag': conv_flag, 'room_id':room_id, 'err_flag':err_flag, 
		'msg':msg, 'beds':beds})	

def validate_room_details(room_id, form, conv_flag):
	err_flag = False
	err_msg = ''

	if conv_flag:
		beds = Bed_conversion.objects.filter(room_id = room_id)
	else:
		beds = Bed.objects.filter(room_id = room_id)
	
	available_min = beds.aggregate(min_date=Min('available_from'))
	available_max = beds.aggregate(max_date=Max('available_to'))
	beds_count = beds.count()
	
	if form.data['available_from']:
		available_from = datetime.datetime.strptime(form.data['available_from'], "%Y-%m-%d").date()
	else:
		err_flag = True
		err_msg = "Available from date is required"
	if form.data['available_to']:
		available_to = datetime.datetime.strptime(form.data['available_to'], "%Y-%m-%d").date()
	else:
		err_flag = True
		err_msg = "Available from date is required"

	if available_min['min_date']:
		if available_from > available_min['min_date']:
			err_flag = True
			err_msg = "Bed availability starts from " + str(available_min['min_date']) + ". Room available from date can't be later than 'Bed' available from date"

	if available_max['max_date']:
		if available_to < available_max['max_date']:
			err_flag = True
			err_msg = "Room available to date can't be earlier than bed available to date"
	if form.data['max_beds'] :
		if int(form.data['max_beds']) < beds_count:
			err_flag = True
			err_msg = "There are already " + str(beds_count) + " beds assigned in this room. So this room can have less than " + str(beds_count) + " beds. Please use Rom Conversion option if this is a conversion."

	return ({'err_flag':err_flag, 'err_msg':err_msg}) 
