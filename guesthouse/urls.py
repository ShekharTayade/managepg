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
	url(r'^ajax/get_availablity_by_element/$', views.get_availablity_by_element, name='get_availablity_by_element'),
	url(r'^ajax/get_block_availablity/$', views.get_block_availablity, name='get_block_availablity'),
	url(r'^ajax/get_floor_availablity/$', views.get_floor_availablity, name='get_floor_availablity'),
	url(r'^ajax/get_room_availablity/$', views.get_room_availablity, name='get_room_availablity'),
	url(r'^ajax/get_bed_availablity/$', views.get_bed_availablity, name='get_bed_availablity'),
	url(r'^ajax/delete_booking/$', views.delete_booking, name='delete_booking'),
	url(r'^change_room_bed/$', views.change_room_bed, name='change_room_bed'),

	#path('booking_form/<str:booking_number>/', views.booking_form, name='booking_form'),
	
	
	path('booking_details_for_payment/<str:receipt_type>', views.booking_details_for_payment, name='booking_details_for_payment'),
	url(r'^payment_receipt/$', views.payment_receipt, name='payment_receipt'),
	url(r'^ajax/choose_booking_for_payment/$', views.choose_booking_for_payment, name='choose_booking_for_payment'),
	path('payment_confirmation/<int:rct_id>/', views.payment_confirmation, name='payment_confirmation'),
	path('payment_confirmation_AR/<str:rct_no>/', views.payment_confirmation_AR, name='payment_confirmation_AR'),
	path('payment_confirmation_pdf/<int:rct_id>/', views.payment_confirmation_pdf, name='payment_confirmation_pdf'),
	path('payment_confirmation_pdf_AR/<str:rct_no>/', views.payment_confirmation_pdf_AR, name='payment_confirmation_pdf_AR'),
	url(r'^print_receipts/$', views.print_receipts, name='print_receipts'),
	url(r'^ajax/get_receipts/$', views.get_receipts, name='get_receipts'),
	url(r'^ajax/get_monthly_adv_rent/$', views.get_monthly_adv_rent, name='get_monthly_adv_rent'),	
	url(r'^ajax/get_net_advance/$', views.get_net_advance, name='get_net_advance'),
	url(r'^ajax/get_bills_for_month/$', views.get_bills_for_month, name='get_bills_for_month'),

	url(r'^bills_receipts_report/$', views.bills_receipts_report, name='bills_receipts_report'),

	
]
	
if settings.DEBUG:
		urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)