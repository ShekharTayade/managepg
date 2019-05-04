from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required
from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta
from num2words import num2words

from django.http import JsonResponse
from django.core.mail import send_mass_mail

from .views import *
from guesthouse.forms import AdvReceiptForm, AdvReceiptForm_AR, ReceiptForm
from guesthouse.models import Guesthouse, Booking, Guest, Room_allocation, Bill, Receipt
from guesthouse.models import Generate_number_by_month, Bed, Room, Floor, Block
from guesthouse.models import Room_allocation, Room_conversion

today = datetime.date.today()

def send_birthday_mails():
	month = datetime.datetime.strftime(today, "%m")
	day = datetime.datetime.strftime(today, "%d")

	bookings = Booking.objects.filter(guest__date_of_birth__month = month, 
		guest__date_of_birth__day = day, guest__email_id__isnull = False) 
	from_mail = "info@nextsteps.co.in"
	
	all_mails = ()
	for b in bookings:	
		mail = ('Happy Birthday', 'Dear ' + b.guest.first_name + ', Wish you many happy returns of the day! SAM Atithi Pavathi wishes that all your wishes come true.', from_mail, [b.guest.email_id])
		m = list(all_mails)
		m.append(mail)
		all_mails = tuple(m)
	
	if len(all_mails) > 0:
		mails_cnt = send_mass_mail(all_mails, fail_silently=False)
	else:
		mails_cnt = 0
	return mails_cnt
	
