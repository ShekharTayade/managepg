from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required
from datetime import datetime
import datetime
from dateutil.relativedelta import relativedelta

from django.core.mail import send_mass_mail
from django.core.mail import send_mail, EmailMultiAlternatives

from django.template.loader import render_to_string
from django.utils.html import strip_tags

from guesthouse.models import Booking, Guesthouse, Bill, Receipt

today = datetime.date.today()

def send_birthday_wishes():

	guesthouse = Guesthouse.objects.get(gh_id = settings.GH_ID)
	
	month = datetime.datetime.strftime(today, "%m")
	day = datetime.datetime.strftime(today, "%d")

	bookings = Booking.objects.filter(guest__date_of_birth__month = month, 
		guest__date_of_birth__day = day, guest__email_id__isnull = False) 
	from_mail = "info@nextsteps.co.in"
	
	
	all_mails = ()
	mails_cnt = 0
	for b in bookings:	
		'''
		mail = ('Happy Birthday', 'Dear ' + b.guest.first_name + ', Wish you many happy returns of the day! SAM Atithi Pavathi wishes that all your wishes come true.', from_mail, [b.guest.email_id])
		m = list(all_mails)
		m.append(mail)
		all_mails = tuple(m)
		'''

		# Send mail
		subject = 'Happy Birthday, ' + b.guest.first_name + ' !'
		html_message = render_to_string('guesthouse/birthday_email.html', 
				{'booking': b, 'guesthouse':guesthouse})
		plain_message = strip_tags(html_message)
		from_email = 'info@nextsteps.co.in'
		to = b.guest.email_id

		#cnt = send_mail(subject, plain_message, from_email, [to], html_message=html_message)

		msg = EmailMultiAlternatives(subject, plain_message, from_email, [to])
		msg.attach_alternative(html_message, "text/html")

		msg.send()	
		mails_cnt = mails_cnt +1

	
	return mails_cnt
	
def send_payment_reminders():
	
	year = str(today.year)
	mth = today.strftime('%m')
	month = year + '-' + mth
	
	rcts = Receipt.objects.filter( 
	bill_id__isnull = False).values_list('bill_id', flat=True)
	
	# Get unpaid bills 
	bills = Bill.objects.filter(bill_for_month = month, amount__gt = 0).exclude(
		bill_number__in = rcts)
	
	mails_cnt = 0
	for b in bills:
		if b.guest.email_id:
		
			guest_name = b.guest.first_name + " " + b.guest.middle_name + b.guest.last_name
			subject = 'Payment Reminder!'
			html_message = render_to_string('guesthouse/payment_reminder.html', 
					{'bill': b, 'guest_name':guest_name})
			plain_message = strip_tags(html_message)
			from_email = 'info@nextsteps.co.in'
			to = b.guest.email_id
			msg = EmailMultiAlternatives(subject, plain_message, from_email, [to])
			msg.attach_alternative(html_message, "text/html")

			msg.send()
			mails_cnt = mails_cnt + 1

	return mails_cnt	
	