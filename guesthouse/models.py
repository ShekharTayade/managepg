from django.db import models


class Country(models.Model):
	country_code = models.CharField(max_length=80, primary_key = True) 
	country_name = models.CharField(max_length=100, blank = True, null=True, unique=True)

	def __str__(self):
		return self.country_code

class State(models.Model):
	state_code = models.CharField(max_length=100, primary_key = True) 
	state_name = models.CharField(max_length=100, blank = True, null=True, unique=True)
	country = models.ForeignKey(Country, models.CASCADE, null=False)

	def __str__(self):
		return self.state_code

class City(models.Model):
	city = models.CharField(max_length=100, primary_key = True) 
	state = models.ForeignKey(State, models.CASCADE, null=False)

	def __str__(self):
		return self.city
	
class Pin_code(models.Model):
	pin_code = models.CharField(primary_key = True, max_length=10, null=False)

	def __str__(self):
		return self.pin_code

class Pin_city_state_country(models.Model):
	pin_code = models.ForeignKey(Pin_code, models.CASCADE, null=False)
	taluk =  models.CharField(max_length=500, null = True)
	city = models.ForeignKey(City, models.CASCADE, null=False) 
	state  = models.ForeignKey(State, models.CASCADE, null=False)
	country  = models.ForeignKey(Country, models.CASCADE, null=False)
	
	class Meta:
		unique_together = ("pin_code", "city", "taluk", "state", "country")

class Guesthouse (models.Model):
	gh_id = models.AutoField(primary_key=True, null=False)
	html_meta_title = models.CharField(max_length = 256, blank=False, unique=True)
	html_meta_name = models.CharField(max_length = 256, blank=True, default='')	
	seo_keywords = models.CharField(max_length = 256, blank=True, default='')	
	gh_name = models.CharField(max_length = 100, blank=False)	
	tag_line = models.CharField(max_length = 50, blank=True, default='')
	show_copyright = models.BooleanField(null=False, default=False)
	copyright_year = models.CharField(max_length = 4, blank=True, default='')
	address1 = models.CharField(max_length = 1000 , blank=True, default='')
	address2 = models.CharField(max_length = 1000 , blank=True, default='')	
	city = models.CharField(max_length = 256 , blank=True, default='')
	state = models.CharField(max_length = 256 , blank=True, default='')	
	zip = models.CharField(max_length = 256 , blank=True, default='')	
	country = models.CharField(max_length = 256 , blank=True, default='')		
	phone_number = models.CharField(max_length = 256 , blank=True, default='')		
	fax_number = models.CharField(max_length = 50 , blank=True, default='')		
	email_id = models.EmailField(blank=True, default='')		
	phone_support_available = models.BooleanField(null=False, default=False)
	support_phone_number = models.CharField(max_length = 50, blank=True, default='')
	phone_support_start_time = models.TimeField(blank=True, null=True)
	phone_support_end_time = models.TimeField(blank=True, null=True)
	phone_support_days = models.CharField(max_length = 50, blank=True, default='')
	show_promotion_section = models.BooleanField(null=False, default=False)
	number_of_promotion_slides = models.IntegerField(null=True, blank=True)
	show_featured_section = models.BooleanField(null=False, default=False)
	featured_header = models.CharField(max_length = 50, blank=True, default='')
	number_of_featured_slides = models.IntegerField(null=True, blank=True)
	month_year_suffix = models.CharField(max_length = 6, null=True) # For generating booking numbers

	def __str__(self):
		return self.gh_name


class Tax (models.Model):
	guesthouse = models.ForeignKey(Guesthouse, models.CASCADE)
	tax_id = models.AutoField(primary_key=True, null=False)
	name = models.CharField(max_length = 128, null=False)
	effective_from = models.DateField(blank=True, null=True)
	effective_to = models.DateField(blank=True, null=True)
	tax_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=False, null=False)

	def __str__(self):
		return self.name 
		
		
class Block(models.Model):
	block_id = models.AutoField(primary_key=True)
	block_name = models.CharField(max_length = 100, blank=False, null=False, unique=True)
	guesthouse = models.ForeignKey(Guesthouse, models.CASCADE, null=False)
	available_from = models.DateField(null=True)
	available_to = models.DateField(null=True)

	def __str__(self):
		return self.block_name
	
	
class Floor(models.Model):
	floor_id = models.AutoField(primary_key=True)
	floor_name = models.CharField(max_length = 100, blank=False, null=False, unique=True)
	block = models.ForeignKey(Block, models.CASCADE, null=False)
	available_from = models.DateField(null=True)
	available_to = models.DateField(null=True)

	def __str__(self):
		return self.floor_name

	
class Room(models.Model):
	room_id = models.AutoField(primary_key=True)
	room_name = models.CharField(max_length = 100, blank=False, null=False, unique=True)
	floor = models.ForeignKey(Floor, models.CASCADE, null=False)
	block = models.ForeignKey(Block, models.CASCADE, null=False)
	available_from = models.DateField(null=True)
	available_to = models.DateField(null=True)
	room_rent = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)
	max_beds = models.IntegerField(null=False)
	advance = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)

	def __str__(self):
		return self.room_name
	
	
class Bed(models.Model):
	bed_id = models.AutoField(primary_key=True)
	bed_name = models.CharField(max_length = 100, blank=False, null=False)
	room = models.ForeignKey(Room, models.CASCADE, null=False)
	floor = models.ForeignKey(Floor, models.CASCADE, null=False)
	block = models.ForeignKey(Block, models.CASCADE, null=False)
	available_from = models.DateField(null=True)
	available_to = models.DateField(null=True)

	def __str__(self):
		return self.bed_name

	
class Food_price(models.Model):
	FOOD_PREF = (
		('VEG', 'Vegetarian'),
		('NOV-VEG', 'Non-Vegetarian'),
	)	
	type = models.CharField(max_length = 7, primary_key=True, null=False, choices=FOOD_PREF, default = "VEG")
	price = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)
	
	
class Guest (models.Model):
	SERVICE = 'SR'
	STUDENT = 'ST'
	OCCUPATION_CHOICES = (
		(SERVICE, 'Working'),
		(STUDENT, 'Studying'),
	)

	GENDER_CHOICES = (
		('MALE', 'Male'),
		('FEMALE', 'Female'),
	)	

	GUARDIAN_TYPE = (
		('FATHER', 'Father'),
		('MOTHER', 'Mother'),
		('HUSBAND', 'Husband'),
		('WIFE', 'Wife'),
		('GUARDIAN', 'Guardian'),
	)	

	
	guest_id = models.AutoField(primary_key=True)
	first_name = models.CharField(max_length = 500, blank=False)
	middle_name = models.CharField(max_length = 500, blank=True, default='')
	last_name = models.CharField(max_length = 500, blank=True, default='')	
	date_of_birth = models.DateField(blank=True, null=True)
	gender = models.CharField(
		max_length=6,
		choices=GENDER_CHOICES,
		default='FEMALE',
	)
	id_card_number = models.CharField(max_length=100, blank=True, default='')
	email_id = models.EmailField(blank=True, default='')
	phone_number = models.CharField(max_length=100, blank=True, default='')
	current_address_1 = models.CharField(max_length=600, blank=True, default='')
	current_address_2 = models.CharField(max_length=600, blank=True, default='')
	current_city = models.CharField(max_length=600, blank=True, default='')
	current_state = models.ForeignKey(State, on_delete = models.DO_NOTHING, blank=True, null=True,  related_name='current_addr_state')
	current_pin_code = models.ForeignKey(Pin_code, on_delete = models.DO_NOTHING, blank=True, null=True, related_name='current_addr_pin_code')
	current_country = models.ForeignKey(Country, on_delete = models.DO_NOTHING, 
		default = 'IND', blank=True, null=True, 
		related_name='current_addr_country')	
	permanent_address_1 = models.CharField(max_length=600, blank=True, default='')
	permanent_address_2 = models.CharField(max_length=600, blank=True, default='')
	permanent_city = models.CharField(max_length=600, blank=True, default='')
	permanent_state = models.ForeignKey(State, on_delete = models.DO_NOTHING, blank=True, null=True,  related_name='permanent_addr_state')
	permanent_pin_code = models.ForeignKey(Pin_code, on_delete = models.DO_NOTHING, blank=True, null=True, related_name='permanent_addr_pin_code')
	permanent_country = models.ForeignKey(Country, on_delete = models.DO_NOTHING, 
		default = 'IND', blank=True, null=True, 
		related_name='permanent_addr_country')	
	occupation = models.CharField(
        max_length=2,
        choices=OCCUPATION_CHOICES,
        default=STUDENT,
    )
	company_name = models.CharField(max_length=600, blank=True, default='')
	company_contact_person = models.CharField(max_length = 600, blank=True, default='')
	company_contact_number = models.CharField(max_length=100, blank=True, default='')
	company_address_1 = models.CharField(max_length=600, blank=True, default='')
	company_address_2 = models.CharField(max_length=600, blank=True, default='')
	company_city = models.CharField(max_length=600, blank=True, default='')
	company_state = models.ForeignKey(State, on_delete = models.DO_NOTHING, blank=True, null=True, related_name='company_addr_state')
	company_pin_code = models.ForeignKey(Pin_code, on_delete = models.DO_NOTHING, blank=True, null=True, related_name='company_addr_pin_code')
	company_country = models.ForeignKey(Country, on_delete = models.DO_NOTHING, 
		default = 'IND', blank=True, null=True, 
		related_name='company_addr_country')
	guest_photo = models.ImageField(upload_to='uploads/%Y/%m/%d/', blank=True, default="")
	blood_group = models.CharField(max_length=10, blank=True, default='')
	allergy_details = models.CharField(max_length=2000, blank=True, default='')
	other_details = models.CharField(max_length=5000, blank=True, default='')
	doctor_to_call = models.CharField(max_length=500, blank=True, default='')
	doctor_contact_number = models.CharField(max_length=500, blank=True, default='')
	referred_by = models.CharField(max_length=500, blank=True, default='')
	referred_by_contact_details = models.CharField(max_length=100, blank=True, default='')
	emergency_contact_1_name = models.CharField(max_length=500, blank=True, default='')
	emergency_contact_1_phone_number = models.CharField(max_length=30, blank=True, default='')
	emergency_contact_2_name = models.CharField(max_length=500, blank=True, default='')
	emergency_contact_2_phone_number = models.CharField(max_length=30, blank=True, default='')
	parent_guardian_1_type = models.CharField(max_length=10, choices=GUARDIAN_TYPE, blank=True, default='')
	parent_guardian_1_name = models.CharField(max_length=500, blank=True, default='')
	parent_guardian_1_qualifications = models.CharField(max_length=500, blank=True, default='')
	parent_guardian_1_occupation = models.CharField(max_length=500, blank=True, default='')
	parent_guardian_1_company = models.CharField(max_length=500, blank=True, default='')
	parent_guardian_1_phone_number = models.CharField(max_length=500, blank=True, default='')
	parent_guardian_1_email_id = models.EmailField(blank=True, default='')
	parent_guardian_2_type = models.CharField(max_length=10, choices=GUARDIAN_TYPE, blank=True, default='')
	parent_guardian_2_name = models.CharField(max_length=500, blank=True, default='')
	parent_guardian_2_qualifications = models.CharField(max_length=500, blank=True, default='')
	parent_guardian_2_occupation = models.CharField(max_length=500, blank=True, default='')
	parent_guardian_2_company = models.CharField(max_length=500, blank=True, default='')
	parent_guardian_2_phone_number = models.CharField(max_length=500, blank=True, default='')
	parent_guardian_2_email_id = models.EmailField(blank=True, default='')
	parent_guardian_3_type = models.CharField(max_length=10, choices=GUARDIAN_TYPE, blank=True, default='')
	parent_guardian_3_name = models.CharField(max_length=500, blank=True, default='')
	parent_guardian_3_qualifications = models.CharField(max_length=500, blank=True, default='')
	parent_guardian_3_occupation = models.CharField(max_length=500, blank=True, default='')
	parent_guardian_3_company = models.CharField(max_length=500, blank=True, default='')
	parent_guardian_3_phone_number = models.CharField(max_length=500, blank=True, default='')
	parent_guardian_3_email_id = models.EmailField(blank=True, default='')	
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)			
	

class Booking (models.Model):

	FOOD_PREF = (
		('VEG', 'Vegetarian'),
		('NOV-VEG', 'Non-Vegetarian'),
	)	
	
	ONE_MONTH = 'ST'
	LONG_TERM = 'LT'
	TENURE = (
			(ONE_MONTH, 'One Month'),
			(LONG_TERM, 'Long Term'),
	)	
	
	booking_number = models.CharField(max_length = 15, primary_key = True)
	guest = models.ForeignKey(Guest, models.DO_NOTHING, null=False)
	guesthouse = models.ForeignKey(Guesthouse, models.DO_NOTHING, null=False)
	check_in_date = models.DateField(null=True, blank=True)
	check_in_time = models.TimeField(null=True, blank=True)
	check_out_date = models.DateField(null=True, blank=True)
	check_out_time = models.TimeField(null=True, blank=True)
	food_option = models.BooleanField(default=False)
	food_preference = models.CharField(max_length = 7, blank=True, choices=FOOD_PREF, default = "VEG")
	tenure = models.CharField(max_length = 2, blank=True, choices=TENURE, default = LONG_TERM)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)			

# This stores history of food choices made by Guest under the same booking
class Booking_food(models.Model):
	FOOD_PREF = (
		('VEG', 'Vegetarian'),
		('NOV-VEG', 'Non-Vegetarian'),
	)	
	booking_number = models.ForeignKey(Booking, models.CASCADE, null=False)
	food_option = models.BooleanField(default=False)
	food_preference = models.CharField(max_length = 7, blank=True, choices=FOOD_PREF, default = "VEG")
	price = models.DecimalField(max_digits=12, decimal_places=2, blank=False, null=False)
	start_date = models.DateTimeField(null=True, blank=True)
	end_date = models.DateTimeField(null=True, blank=True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)		
	
class Room_allocation(models.Model):
	alloc_id = models.AutoField(primary_key=True)
	booking = models.ForeignKey(Booking, models.CASCADE, null=False)
	guest = models.ForeignKey(Guest, models.CASCADE, null=False)
	bed = models.ForeignKey(Bed, models.PROTECT, null=True, blank=True)
	room = models.ForeignKey(Room, models.PROTECT, null=True, blank=True)
	floor = models.ForeignKey(Floor, models.PROTECT, null=True, blank=True)
	block = models.ForeignKey(Block, models.PROTECT, null=True, blank=True)
	allocation_start_date = models.DateTimeField(null=True, blank=True)
	allocation_end_date = models.DateTimeField(null=True, blank=True)
	created_date = models.DateTimeField(auto_now_add=True, null=False)	
	updated_date = models.DateTimeField(auto_now=True, null=False)			

	
class Generate_number_by_month(models.Model):
	type = models.CharField(max_length = 50, null=False, primary_key = True)
	description = models.CharField(max_length = 1000, null=True)
	month_year = models.CharField(max_length = 6, null=False)
	current_number = models.IntegerField(null=False)
	

	