import datetime
from django.db import models

class CraigsListSite(models.Model):
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
	craigs_list_site = models.ForeignKey(CraigsListSite)
	full_ad_text = models.TextField()
	def __unicode__(self):
		return self.full_ad_text;
