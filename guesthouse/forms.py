from django import forms
from django.contrib.auth.models import User

#from NextSteps.validators import validate_NextSteps_email, validate_contact_name
#from NextSteps.validators import validate_image_size, validate_india_mobile_no

from django.core.validators import validate_slug, MinLengthValidator
from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField
from django.utils.translation import gettext_lazy as _

from string import Template
from django.utils.safestring import mark_safe
from django.forms import ImageField

from guesthouse.models import Booking, Guest, Room_allocation, Pin_code
from guesthouse.models import Receipt, Bill, Vacate

from guesthouse.validators import validate_image_size, validate_india_mobile_no, validate_yyyy_mm

class BookingForm(forms.ModelForm):

	booking_number = forms.CharField(
		widget=forms.TextInput(),
		required=False
	)	

	guest = forms.CharField(
		widget=forms.TextInput(),
		required=False
	)	

	guesthouse = forms.CharField(
		widget=forms.TextInput(),
		required=False
	)		


	class Meta:
		model = Booking
		exclude = ('booking_number', 'guest', 'guesthouse')


class GuestForm(forms.ModelForm):

	guest_id = forms.IntegerField(
		required=False
	)

        
	guest_photo = forms.ImageField(
		validators=[validate_image_size],
		required=False
	)
	
	current_address_1 = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Flat / House No./ Floor / Building'}),
		required=False
	) 
	current_address_2 = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Colony / Street / Locality'}),
		required=False
	) 
	current_pin_code = forms.CharField(
		widget=forms.TextInput(),
		required=False
	)	
	
	permanent_address_1 = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Flat / House No./ Floor / Building'}),
		required=False
	) 
	permanent_address_2 = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Colony / Street / Locality'}),
		required=False
	) 
	permanent_pin_code = forms.CharField(
		widget=forms.TextInput(),
		required=False
	)	
	company_address_1 = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Flat / House No./ Floor / Building'}),
		required=False
	) 
	company_address_2 = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Colony / Street / Locality'}),
		required=False
	) 
	company_pin_code = forms.CharField(
		widget=forms.TextInput(),
		required=False
	)	
	

	phone_number = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Mobile/Landline(with STD code)'}),
		required=False
	)	
	company_contact_number = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Mobile/Landline(with STD code)'}),
		required=False
	)	
	doctor_contact_number = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Mobile/Landline(with STD code)'}),
		required=False
	)	
	parent_guardian_1_phone_number = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Mobile/Landline(with STD code)'}),
		required=False
	)	
	parent_guardian_2_phone_number = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Mobile/Landline(with STD code)'}),
		required=False
	)	
	parent_guardian_3_phone_number = forms.CharField(
		widget=forms.TextInput(attrs={'placeholder': 'Mobile/Landline(with STD code)'}),
		required=False
	)	
	
	
	class Meta:
		model = Guest
		exclude = ('current_pin_code', 'permanent_pin_code', 'company_pin_code')

		
class Room_allocationForm(forms.ModelForm):
	
	alloc_id = forms.CharField(
		widget=forms.TextInput(),
		required=False
	)	
	booking = forms.CharField(
		widget=forms.TextInput(),
		required=False
	)	

	guest = forms.CharField(
		widget=forms.TextInput(),
		required=False
	)


	class Meta:
		model = Room_allocation
		exclude = ('booking', 'guest')

		
class AdvReceiptForm(forms.ModelForm):
	id = forms.CharField(
		widget=forms.TextInput(),
		required=False
	)	
	guest = forms.CharField(
		widget=forms.TextInput(),
		required=False
	)	
	booking = forms.CharField(
		widget=forms.TextInput(),
		required=False
	)	
	receipt_number = forms.CharField(
		widget=forms.TextInput(),
		required=False,
		help_text='Auto Generated'
	)
	bill = forms.CharField(
		widget=forms.Select(),
		required=False,
		help_text='Payment bill against which payment is being made'
	)	
	receipt_for_month = forms.CharField(
		widget=forms.TextInput(),
		required=False,
		help_text='YYYY-MM (Ex. 2019-01)',
		validators=[validate_yyyy_mm]
	)	
	
	class Meta:
		model = Receipt
		exclude = ('guest', 'booking')
		
	def clean_bill(self):
		bill = self.cleaned_data['bill']

		try:
			billObj = Bill.objects.get(pk = bill)
		except Bill.DoesNotExist:
			billObj = None

		return billObj



class AdvReceiptForm_AR(forms.ModelForm):
	id = forms.CharField(
		widget=forms.TextInput(),
		required=False
	)	
	guest = forms.CharField(
		widget=forms.TextInput(),
		required=False
	)	
	booking = forms.CharField(
		widget=forms.TextInput(),
		required=False
	)	
	receipt_number = forms.CharField(
		widget=forms.TextInput(),
		required=False,
		help_text='Auto Generated'
	)
	bill = forms.CharField(
		widget=forms.Select(),
		required=False,
		help_text='Payment bill against which payment is being made'
	)	
	receipt_for_month1 = forms.CharField(
		widget=forms.TextInput(),
		required=False,
		help_text='YYYY-MM (Ex. 2019-01)',
		validators=[validate_yyyy_mm]
	)	
	receipt_for_month2 = forms.CharField(
		widget=forms.TextInput(),
		required=False,
		help_text='YYYY-MM (Ex. 2019-02)',
		validators=[validate_yyyy_mm]
	)	
	receipt_for_month3 = forms.CharField(
		widget=forms.TextInput(),
		required=False,
		help_text='YYYY-MM (Ex. 2019-03)',
		validators=[validate_yyyy_mm]
	)	
	receipt_for_month4 = forms.CharField(
		widget=forms.TextInput(),
		required=False,
		help_text='YYYY-MM (Ex. 2019-04)',
		validators=[validate_yyyy_mm]
	)	
	
	class Meta:
		model = Receipt
		exclude = ('guest', 'booking')
		
	def clean_bill(self):
		bill = self.cleaned_data['bill']

		try:
			billObj = Bill.objects.get(pk = bill)
		except Bill.DoesNotExist:
			billObj = None

		return billObj		

class Vacate_form(forms.ModelForm):
	class Meta:
		model = Vacate
		exclude = ('vacate_id',)	
		
		