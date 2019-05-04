from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from guesthouse.models import Employee

def user_is_manager(function):
	def wrap(request, *args, **kwargs):
		try:
			userObj = User.objects.get(username = request.user)
		except User.DoesNotExist:
			userObj = None
		if userObj:
			try:
				if userObj.employee.is_manager or userObj.is_staff:
					return function(request, *args, **kwargs)
				else:
					raise PermissionDenied
			except Employee.DoesNotExist:
					raise PermissionDenied
		else:
			raise PermissionDenied
	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap