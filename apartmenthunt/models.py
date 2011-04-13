import datetime
from django.db import models

class CraigslistSite(models.Model):
	''' A class representing the apartments website of a craigslist subdomain.'''
	site_name = models.CharField(max_length=64)
	site_subdomain = models.CharField(max_length=64)
	last_collection_date = models.DateTimeField('last collection date')
	def __unicode__(self):
		return self.site_name;
	def was_collected_today(self):
		return self.last_collection_date.date() == datetime.date.today()

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
