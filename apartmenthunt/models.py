import datetime
from django.db import models

class CraigslistSite(models.Model):
	''' A class representing the apartments website of a craigslist subdomain.'''
	site_name = models.CharField(max_length=64)
	site_subdomain = models.CharField(max_length=64)
	last_collection_date = models.DateTimeField('last collection date')
	def __unicode__(self):
		return self.site_name;

class Apartment(models.Model):
	''' A class representing an ad for an apartment.'''
	craigslist_site = models.ForeignKey(CraigslistSite)
	listing_number = models.CharField(max_length=16, unique=True)
	information_extracted = models.BooleanField(default=False)
	listing_datetime = models.DateTimeField(null=True)
	price = models.IntegerField(null=True)
	num_bedrooms = models.IntegerField(null=True)
	num_bathrooms = models.DecimalField(max_digits=2, decimal_places=1, null=True)
	title = models.CharField(max_length=128, null=True)
	title_address = models.CharField(max_length=128, null=True)
	street_address = models.CharField(max_length=128, null=True)
	city = models.CharField(max_length=32, null=True)
	state = models.CharField(max_length=32, null=True)
	cats_allowed = models.BooleanField(default=False)
	dogs_allowed = models.BooleanField(default=False)
	full_ad_text = models.TextField()
	def __unicode__(self):
		return self.title;

def get_apartments_from_search(site, filter):
	''' Gets the apartments that match the specified filter. '''
	
	# If there's no filter, return all apartments.
	if 'submit' not in filter:
		return Apartment.objects.filter(craigslist_site=site.id), None
	
	INT_MAX = 2**30
	
	# Check that there are no errors in the search filter.
	errors = validate_search_filter(filter)
	if len(errors) > 0:
		return None, errors
	
	# Check the price.
	price_min = filter['price_min']
	price_max = filter['price_max']
	
	# Check the number of bedrooms.
	if filter['bedrooms'] == 'all':
		bedrooms_min = 0
		bedrooms_max = INT_MAX
	elif filter['bedrooms'] == '4':
		bedrooms_min = 4
		bedrooms_max = INT_MAX
	else:
		bedrooms_min = filter['bedrooms']
		bedrooms_max = filter['bedrooms']
	
	# Check the number of bathrooms.
	if filter['bathrooms'] == 'all':
		bathrooms_min = 0
		bathrooms_max = INT_MAX
	elif filter['bathrooms'] == '3':
		bathrooms_min = 3
		bathrooms_max = INT_MAX
	else:
		bathrooms_min = filter['bathrooms']
		bathrooms_max = filter['bathrooms']
	
	# Get preliminary result.
	result = Apartment.objects.filter(
		craigslist_site=site.id).filter(
		price__gte=price_min).filter(
		price__lte=price_max).filter(
		num_bedrooms__gte=bedrooms_min).filter(
		num_bedrooms__lte=bedrooms_max).filter(
		num_bathrooms__gte=bathrooms_min).filter(
		num_bathrooms__lte=bathrooms_max)
	
	# Check if dogs should be allowed.
	if 'dogs_allowed' in filter and filter['dogs_allowed'] == 'on':
		result = result.filter(dogs_allowed=1)
	
	# Check if cats should be allowed.
	if 'cats_allowed' in filter and filter['cats_allowed'] == 'on':
		result = result.filter(cats_allowed=1)
	
	# Return the apartments that match the filter.
	return result, None

def validate_search_filter(filter):
	''' Check that all required filter values are specified correctly. '''
	
	PRICE_MIN = 0
	PRICE_MAX = 10000
	
	errors = []
	
	if 'price_min' not in filter:
		errors.append('Please specify a minimum rent.')
	else:
		try:
			i = int(filter['price_min'])
			if i <= PRICE_MIN:
				errors.append('Please enter a minimum rent greater than zero.')
			elif i >= PRICE_MAX:
				errors.append('Please enter a minimum rent less than $10,000.')
		except ValueError:
			errors.append('Please enter an integer for the minimum rent.')
	if 'price_max' not in filter:
		errors.append('Please specify a maximum rent.')
	else:
		try:
			i = int(filter['price_max'])
			if i <= PRICE_MIN:
				errors.append('Please enter a maximum rent greater than zero.')
			elif i >= PRICE_MAX:
				errors.append('Please enter a maximum rent less than $10,000.')
		except ValueError:
			errors.append('Please enter an integer for the maximum rent.')
	if 'price_min' in filter and 'price_max' in filter and filter['price_max'] < filter['price_min']:
		errors.append('Please enter a maximum rent that is greater than the minimum rent.')
	if 'bedrooms' not in filter:
		errors.append('Please specify the number of bedrooms.')
	if 'bathrooms' not in filter:
		errors.append('Please specify the number of bathrooms.')
	
	return errors
