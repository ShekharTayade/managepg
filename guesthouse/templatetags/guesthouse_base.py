from datetime import datetime
import datetime
from django.shortcuts import render, get_object_or_404
from django.db import IntegrityError, DatabaseError, Error
from django.db.models import Count
from django.contrib.auth.models import User

from django.http import HttpResponse
from django.conf import settings

from django import template

today = datetime.date.today()

register = template.Library()
@register.inclusion_tag('guesthouse/topbar.html')
def topbar(request , auth_user):

	return {'request':request, 'user': request.user}


@register.inclusion_tag('guesthouse/eStore_admin_menu.html')
def admin_menu(request):

	return {'request':request, 'user': request.user}	
	

@register.inclusion_tag('guesthouse/main_slider.html')
def main_slider(request):

	return {'request':request, 'user': request.user}	

@register.inclusion_tag('guesthouse/advantages.html')
def advantages(request):

	return {'request':request, 'user': request.user}	
	
@register.inclusion_tag('guesthouse/footer.html')	
def site_footer(request):

	return {'request':request, 'user': request.user}

		
@register.inclusion_tag('guesthouse/copy_right.html')	
def copy_right(request):

	return {'request':request, 'user': request.user}

