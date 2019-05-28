from django.contrib.auth import authenticate, login, get_user
from django.contrib.auth import login as auth_login
from django.shortcuts import get_object_or_404, render, redirect

from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, DatabaseError, Error

from django.urls import resolve
from django.contrib import messages

from guesthouse.models import Employee
   
def guesthouselogin(request):

	if request.method == 'POST':
    
		# Get current session details
		sessionid = request.session.session_key
	
		
		username = request.POST['username'] 
		password = request.POST['password']
		email = request.POST['email']
		next = request.POST['curr_pg']
		

		user = authenticate(request, email=email, username=username, password=password)
       
		if user is not None :
            
			login(request, user)
			
			if not request.POST.get('remember', None):
				request.session.set_expiry(0)   
	
			return redirect(next)
        
		else :
			messages.add_message(request, messages.ERROR, 'Your credentials did not match. Please try again.')		
			return redirect(next)
			#return render(request, 'eStore/estore_base.html', {
			#	'username' : request.user.username, 'auth_user' : 'FALSE'})
	else:
		# This is required as front checks for message object and displays
		# login dialog box only when the message objects is present
		if not request.user.is_authenticated:
			messages.add_message(request, messages.INFO, 'Nothing')		
		
		return render(request, 'guesthouse/guesthouse_base.html')

def is_manager(user):
	
	return user.employee.is_manager or user.is_staff

def is_ceo(user):
	
	return user.employee.is_manager or user.is_staff or user.employee.is_ceo
	
	
