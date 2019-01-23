from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import re


def validate_email(value):

    if not "NextSeps.com" in value:
        raise ValidationError(_('The email is invalid. All emails have to be registered on this domain only.'))

def validate_contact_name(value):

    regex = r'^[\w.@+-]+$'
    isValid = re.match(regex, value)
  
    if not isValid:
         raise ValidationError(_('Enter a valid name. It may contain only English letters, '
        'numbers, and @/./+/-/_ characters.'))
     
def validate_image_size(value):
    limit = 50 * 1024
    if value.size > limit:
         raise ValidationError(_('Please upload image with size <= 50KB.'))
        
def validate_max100(value):
    
    if value > 100 :
         raise ValidationError(_('Please enter a value less than 100 %.'))

def validate_max24hrs(value):
    
    if value > 24 :
         raise ValidationError(_('Please enter a value less than 24 hr.'))

def validate_max7days(value):

    if value > 7 :
         raise ValidationError(_('Please enter a value less than 7 days.'))

def validate_india_mobile_no (value):
    regex = r'^[6-9]\d{9}$'
    isValid = re.match(regex, value)
  
    if not isValid:
         raise ValidationError(_('Please enter 10-digit mobile number without prefix +91 or 0'))
    