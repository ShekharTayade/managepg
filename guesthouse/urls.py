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
	path('booking_form/<str:booking_number>/', views.booking_form, name='booking_form'),
	
	
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
	path('receipt_modify/<int:rct_id>/', views.receipt_modify, name='receipt_modify'),
	url(r'^ajax/get_receipt/$', views.get_receipt, name='get_receipt'),
	url(r'^ajax/delete_receipt/$', views.delete_receipt, name='delete_receipt'),

	
	url(r'^vacate_booking/$', views.vacate_booking, name='vacate_booking'),
	path('vacate_form/<str:booking_number>/', views.vacate_form, name='vacate_form'),
	url(r'^vacate_confirm/$', views.vacate_confirm, name='vacate_confirm'),
	path('vacate_print/<int:vacate_id>/', views.vacate_print, name='vacate_print'),
	url(r'^set_vacate_date/$', views.set_vacate_date, name='set_vacate_date'),

	url(r'^blocking_details/$', views.blocking_details, name='blocking_details'),
	url(r'^ajax/get_blocking/$', views.get_blocking, name='get_blocking'),
	url(r'^ajax/cancel_blocking/$', views.cancel_blocking, name='cancel_blocking'),
	

	url(r'^bills_receipts_report/$', views.bills_receipts_report, name='bills_receipts_report'),
	url(r'^room_occupancy_report/$', views.room_occupancy_report, name='room_occupancy_report'),
	url(r'^ajax/get_bed_occupant_details/$', views.get_bed_occupant_details, name='get_bed_occupant_details'),
	url(r'^guest_account_booking/$', views.guest_account_booking, name='guest_account_booking'),
	path('guest_account_report/<str:booking_number>/', views.guest_account_report, name='guest_account_report'),
	url(r'^booking_report/$', views.booking_report, name='booking_report'),
	url(r'^ajax/booking_report_Table/$', views.booking_report_table, name='booking_report_table'),
	url(r'^waiting_list/$', views.waiting_list, name='waiting_list'),	
	url(r'^monthly_due_bills_report/$', views.monthly_due_bills_report, name='monthly_due_bills_report'),	
	url(r'^monthly_due_bills_table/$', views.monthly_due_bills_table, name='monthly_due_bills_table'),	
	url(r'^monthly_bills_receipts_report/$', views.monthly_bills_receipts_report, name='monthly_bills_receipts_report'),	
	url(r'^monthly_bills_receipts/$', views.monthly_bills_receipts, name='monthly_bills_receipts'),	
	url(r'^vacate_report/$', views.vacate_report, name='vacate_report'),
	url(r'^ajax/vacate_report_Table/$', views.vacate_report_table, name='vacate_report_table'),


	
	url(r'^print_bills/$', views.print_bills, name='print_bills'),
	url(r'^ajax/get_bills/$', views.get_bills, name='get_bills'),
	url(r'^ajax/get_bill/$', views.get_bill, name='get_bill'),
	url(r'^ajax/delete_bill/$', views.delete_bill, name='delete_bill'),
	path('bill_form/<str:bill_number>/', views.bill_form, name='bill_form'),
	path('bill_modify_confirmation/<str:bill_number>/', views.bill_modify_confirmation, name='bill_modify_confirmation'),
	url(r'^generate_bills/$', views.bills_for_month, name='bills_for_month'),
	url(r'^ajax/generate_bill_month/$', views.generate_bill_month, name='generate_bill_month'),
	
	url(r'^room_conversion/$', views.room_conversion, name='room_conversion'),
	url(r'^ajax/get_floors_by_block/$', views.get_floors_by_block, name='get_floors_by_block'),
	url(r'^ajax/get_rooms_by_floor/$', views.get_rooms_by_floor, name='get_rooms_by_floor'),
	url(r'^ajax/get_beds_by_room/$', views.get_beds_by_room, name='get_beds_by_room'),
	url(r'^ajax/get_room_conversion/$', views.get_room_conversion, name='get_room_conversion'),
	url(r'^ajax/get_room_details/$', views.get_room_details, name='get_room_details'),
	url(r'^ajax/room_form/$', views.room_form, name='room_form'),
	url(r'^ajax/room_conv_form/$', views.room_conv_form, name='room_conv_form'),
	path('convert_room/<int:room_id>/', views.convert_room, name='convert_room'),
	path('room_conversion_confirmation/<int:room_id>/', views.room_conversion_confirmation, name='room_conversion_confirmation'),
	url(r'^ajax/cancel_conversion/$', views.cancel_conversion, name='cancel_conversion'),

	url(r'^manage_room/$', views.manage_room, name='manage_room'),
	url(r'^ajax/room_detailsForm/$', views.room_detailsForm, name='room_detailsForm'),
	url(r'^room_modify/$', views.room_modify, name='room_modify'),

	url(r'^search_booking_vac_period/$', views.search_booking_vac_period, name='search_booking_vac_period'),
	path('vac_period/<str:booking_number>/', views.vac_period, name='vac_period'),

]
	
if settings.DEBUG:
		urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)