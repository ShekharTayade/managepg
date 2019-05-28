from django.core.management.base import BaseCommand, CommandError
from guesthouse.views.send_mail import send_payment_reminders, send_birthday_wishes


class Command(BaseCommand):

	help = "Send birthday wishes."

	def handle(self, *args, **options):
		err_flag = False
		try:
			mail_cnt = send_birthday_wishes()
		except Exception as e:
			print (type(e)) 
			print (e) 
			err_flag = True
		
		if err_flag:
			self.stderr.write(self.style.SUCCESS('Error occured while sending birthday wishes.'))
		else :
			self.stdout.write(self.style.SUCCESS('Successfully sent ' + str(mail_cnt) + ' brithday wishes.'))
