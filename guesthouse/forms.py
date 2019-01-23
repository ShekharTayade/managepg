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

from guesthouse.models import Booking, Guest
from guesthouse.validators import validate_image_size, validate_india_mobile_no

class BookingForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = '__all__'
		
		#['first_name', 'middle_name',, 'last_name',
		#		'date_of_birth', 'gender', 'email_id'
		#		'phone_number', 'current_address_1', 'current_address_2',
		#		'current_address_city', 'current_address_state', 'current_address_pin_code',
		#		'current_address_country', 'permanent_address_1', 'permanent_address_2',
		#		'permanent_address_city', 'permanent_address_state', 'permanent_address_pin_code',
		#		'permanent_address_country', 
        #          ]

class GuestForm(forms.ModelForm):
        
    guest_photo = forms.ImageField(
        validators=[validate_image_size],
        required=False
    )

    class Meta:
        model = Guest
        fields = '__all__'
