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
from guesthouse.validators import validate_image_size, validate_india_mobile_no

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

	#def __init__(self, data=None, *args, **kwargs):
	#	super(GuestForm, self).__init__(*args, **kwargs)
	#	import pdb
	#	pdb.set_trace()
	#	if data is not None:
	#		data = data.copy() # make it mutable
	#		if data['guest-current_pin_code']:
	#			try: 
	#				obj = Pin_code.objects.get(pin_code=data['guest-current_pin_code'])
	#				data['guest-current_pin_code'] = obj
	#			except Pin_code.DoesNotExists:
	#				None

		
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
