from django import template


register = template.Library()

@register.filter
def multiply(a, b):
    return a*b

@register.filter
def subtract(a, b):
    return a-b
	
	
@register.filter
def month_name(month):
	if not month or month == '':
		return ''
		
	idx = month.find("-")
	year = month[:idx]
	month_num = int(month[(idx+1):])
	
	months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
	
	return months[month_num-1] +"-" + year
	

@register.filter
def minus_tax(value, tax_rate):
	if not tax_rate or tax_rate == '':
		return 0
	return round( float(value) / (1 + (float(tax_rate)/100)), 2 )

@register.filter	
def tax(value, tax_rate):
	if not tax_rate or tax_rate == '':
		return 0
 
	return float(value) - round( float(value) / (1 + (float(tax_rate)/100)), 2 )