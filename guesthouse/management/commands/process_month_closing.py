from django.core.management.base import BaseCommand, CommandError
from guesthouse.views import *
from guesthouse.models import Booking, Bill
from guesthouse.models import Receipt, Closing_balance
from guesthouse.models import Month_closing_error


class Command(BaseCommand):

	help = "Generate current month bills and process previous month closing"

	def handle(self, *args, **options):
		today = datetime.datetime.today()

		# If no month is provided, default to the current month
		#if not options['month']:
		year = str(today.year)
		mth = today.strftime('%m')
		month = year + '-' + mth
		#else :
		#	month = options['month'][0]

		print(month)
			
		# Generate Bills for current month
		err_flag = False
		bill_generation = generate_month_bills(month)
		if bill_generation == True:		
			raise self.stderr.write(self.style.SUCCESS("An Error Occured in Billing"))
			return

		##########################################
		###### The closing is for previous month
		##########################################
		prev_month = datetime.datetime.strptime(month + '-01', "%Y-%m-%d").date() + relativedelta(months=-1)
		## Set month to the previous month
		month = datetime.datetime.strftime(prev_month, "%Y-%m")
		
		## 1st of the month to be processed
		curr_month_1st =  datetime.datetime.strptime(month + '-01', "%Y-%m-%d").date()

		# Get all bookings valid during the  month
		bookings = Booking.objects.filter( 
			Q(check_out_date__isnull = True) | Q(check_out_date__gte = curr_month_1st) )
		
		rct_types_for_billing = ['RN', 'FD', 'AR', 'OT']  # not considering the advance paid for the monthly calculations
		for b in bookings:

			# Check if closing is already done for the month, booking
			curr_cls = Closing_balance.objects.filter(booking = b, closing_balance_month = month)
			
			# perform closing only if not already done
			if curr_cls.count() == 0:
				bills = Bill.objects.filter(booking = b).aggregate(bill_sum=Sum('amount'))
				rcts = Receipt.objects.filter(
					booking = b, receipt_for__in = rct_types_for_billing).aggregate(rct_sum=Sum('amount'))
				
				if bills['bill_sum'] and rcts['rct_sum']:
					balance = Decimal( bills['bill_sum'] - rcts['rct_sum'] )
				else:
					balance = Decimal(0)
				
				# update the closing balance as of the month
				try:
					closing = Closing_balance(
						guest = b.guest,
						booking = b,
						closing_balance_month = month,
						amount = balance,
						created_date = today,	
						updated_date = today
					)
					closing.save()
				except Exception as error:
					err_flag = True
					print (error)
					err = Month_closing_error (
						guest = b.guest,
						booking = b,
						closing_balance_month = month,
						amount = closing_balance,
						error = error,
						created_date = today,	
						updated_date = today
					)
					err.save()
		if not err_flag:
			self.stdout.write(self.style.SUCCESS('Successfully performed bill generation and month closing'))
		else :
			self.stderr.write(self.style.SUCCESS('Month closing process ended with errors.'))
		