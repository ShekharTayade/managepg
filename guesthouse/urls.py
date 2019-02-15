from django.urls import path
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from allauth.account.views import LoginView


from . import views

urlpatterns =[
	url(r'^$', views.index, name='index'),	

	url(r'^accounts/', include('allauth.urls')),
	url(r'^login/$', views.guesthouselogin, name='login'),	
	url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),

	url(r'^password/$', auth_views.PasswordChangeView.as_view(template_name='password_change.html'), name='password_change'),    
	url(r'^password/done/$', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),
	
	url(r'^reset/$', auth_views.PasswordResetView.as_view(
		template_name='password_reset.html',
		email_template_name='password_reset_email.html',
		subject_template_name='password_reset_subject.txt'), name='password_reset'),
	url(r'^reset/done/$', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
	url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
	   auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
	   name='password_reset_confirm'),
	url(r'^reset/complete/$',
	   auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
	   name='password_reset_complete'), 

	url(r'^new_booking/$', views.new_booking, name='new_booking'),
	url(r'^ajax/get_addr_pin_city_state/$', views.get_addr_pin_city_state, name='get_addr_pin_city_state'),	
	url(r'^manage_booking/$', views.manage_booking, name='manage_booking'),
	url(r'^ajax/get_bookings/$', views.get_bookings, name='get_bookings'),
	url(r'^ajax/get_booking_by_number/$', views.get_booking_by_number, name='get_booking_by_number'),
	
]
	
if settings.DEBUG:
		urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)