from django.shortcuts import render, get_object_or_404
from datetime import datetime
import datetime
from django.db import IntegrityError, DatabaseError, Error

from django.http import HttpResponse
from django.conf import settings


def index(request):

	return render(request, "guesthouse/guesthouse_base.html",{})

	
def register(request):
	
	return render(request, "guesthouse/register.html")

def contact_us(request):

	return render(request, "guesthouse/contact_us.html")

def about_us(request):

	return render(request, "guesthouse/about_us.html")
	