from django.shortcuts import render, get_object_or_404
from datetime import datetime
import datetime
from django.db import IntegrityError, DatabaseError, Error
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse

from guesthouse.models import Pin_code, City , State, Country, Pin_city_state_country


def index(request):

	return render(request, "guesthouse/guesthouse_base.html",{})

	
def register(request):
	
	return render(request, "guesthouse/register.html")

def contact_us(request):

	return render(request, "guesthouse/contact_us.html")

def about_us(request):

	return render(request, "guesthouse/about_us.html")
	
	
	
@csrf_exempt					
def get_addr_pin_city_state(request):

	ipin_code = request.POST.get('pin_code', None)
	
	pin_code = {}
	city = {}
	cstate = {}
	country = {}
	
	if ipin_code :
		pin_codeObj = Pin_code.objects.filter(pin_code = ipin_code)
		pin_code = pin_codeObj.values("pin_code").distinct()
		city = Pin_city_state_country.objects.filter(pin_code__in = pin_codeObj).values("city").distinct()
		cstate = Pin_city_state_country.objects.filter(pin_code__in = pin_codeObj).values("state").distinct()
		country = Pin_city_state_country.objects.filter(pin_code__in = pin_codeObj).values("country__country_name").distinct()
	else :
		pin_code = Pin_city_state_country.objects.values("pin_code").distinct()
		city = Pin_city_state_country.objects.values("city").distinct()
		cstate = Pin_city_state_country.objects.values("state").distinct()
		country = Pin_city_state_country.objects.values("country__country_name").distinct()

		
	return( JsonResponse({'pin_code':list(pin_code), 'city':list(city), 'cstate':list(cstate),
			'country':list(country)}, safe=False) )		


@csrf_exempt
def validate_address(request):
	ipin_code = request.POST.get('pin_code', None)
	icity = request.POST.get('city', None)
	icstate = request.POST.get('cstate', None)
	icountry = request.POST.get('country', None)

	msg = []
	err_flag = False

	if ipin_code is None or ipin_code == '':
		msg.append("Pin code cannot be empty")
		# Pin Code can be left null
		
	if icity is None or icity == '':
		msg.append("City cannot be empty")
		err_flag = True
	if icstate is None or icstate == '':
		msg.append("State cannot be empty")
		err_flag = True
	if icountry is None or icountry == '':
		msg.append("Country cannot be empty")
		err_flag = True
	
	q = Pin_city_state_country.objects.all()
	
	if ipin_code:
		q = q.filter(pin_code_id = ipin_code)
	if icity:
		q = q.filter(city_id = icity)
	if icstate:
		q = q.filter(state_id = icstate)
	if icity:
		cnt = Country.objects.filter(country_name = icountry).first()
		q = q.filter(country = cnt)
	
	if q is None or q.count() == 0:
		msg.append("Entered Pin code, City, State is invalid. Please correct and then proceed.")
		err_flag = True

	if not err_flag:
		msg.append("SUCCESS")
	
	return JsonResponse({'msg':msg})
