from django.conf import settings
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db.models import Count, Q, Max, Sum
from django.db.models import ProtectedError

import requests
import datetime

from guesthouse.models import Bill, Receipt

today = datetime.datetime.today()

FAST2SMS_URL = "https://www.fast2sms.com/dev/bulk"
API_KEY = ''

# Send SMSs on 10th of the month
def send_payment_reminder_10():
	if today.day() == 10:
		year = str(today.year)
		mth = today.strftime('%m')
		this_month = year + '-' + mth
			
		rcts_with_bill_ids = Receipt.objects.filter( 
				receipt_for_month = this_month, bill_id__isnull = False, amount__gt = 0,
				booking__account_closed = False).exclude(
				receipt_for__in =['AD', 'BK']).values_list(
				'bill_id', flat=True)
		
		# All Bills without receipts
		bills_without_receipts = Bill.objects.filter(
				bill_for_month = this_month, amount__gt = 0,
				booking__account_closed = False).exclude(
				bill_number__in = rcts_with_bill_ids)						
		
		for b in bills_without_receipts:
			phone_number = b.guest.phone_number
			if phone_number:
				sms_msg = "Payment of " + str(b.amount) + " towards " + b.get_bill_for_display() + " for the month of " + this_month + " is pending. Please pay immediately."
				payload = "sender_id=FSTSMS&message=" + sms_msg + "&language=english&route=t&numbers=" + str(phone_number)
				headers = {
					'authorization': "API_KEY",
					'Content-Type': "application/x-www-form-urlencoded",
					'Cache-Control': "no-cache",
					}

				response = requests.request("POST", FAST2SMS_URL, data=payload, headers=headers)

				print(response.text)
				
def send_test_sms(phone_number):
	payload = "sender_id=FSTSMS&message=This%20is%20a%20test%20message&language=english&route=t&numbers=" + str(phone_number)
	headers = {
		'authorization': "API_KEY",
		'Content-Type': "application/x-www-form-urlencoded",
		'Cache-Control': "no-cache",
		}

	response = requests.request("POST", FAST2SMS_URL, data=payload, headers=headers)

	print(response.text)	