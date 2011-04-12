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
	listing_number = models.CharField(max_length=16)
	price = models.IntegerField(default=0)
	num_bedrooms = models.IntegerField(default=0)
	num_bathrooms = models.DecimalField(max_digits=2, decimal_places=1, default=0.0)
	title = models.CharField(max_length=128, default='')
	address = models.CharField(max_length=256, default='')
	cats_allowed = models.BooleanField(default=False)
	dogs_allowed = models.BooleanField(default=False)
	full_ad_text = models.TextField()
	def __unicode__(self):
		return self.title;
