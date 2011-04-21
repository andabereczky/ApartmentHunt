from datetime import datetime
from django.http import HttpResponse
from django.template import Context, loader
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response, get_object_or_404
from apartmenthunt.models import CraigslistSite, Apartment, get_apartments_from_search
import crawler

def index(request):
	
	# Get all Craigslist sites in the database, ordered alphabetically.
	sites = CraigslistSite.objects.all().order_by('site_name')
	
	# Set up the context (i.e. a dictionary mapping template variable names to
	# Python objects)
	context = Context({
		'sites': sites,
	})
	
	# Render the page.
	return render_to_response('apartmenthunt/index.html', context)

def search(request, craigslist_site_subdomain):
	
	# Get the specified Craigslist site from the database.
	site = get_object_or_404(CraigslistSite, site_subdomain=craigslist_site_subdomain)
	
	# Get the number of apartments for this site.
	num_apartments_old = Apartment.objects.filter(craigslist_site=site.id).count()
	
	# Download new data from Craigslist.
	crawler.crawl(site)
	
	# Delete all expired listings from the database.
	# TODO: implement
	
	# Get the number of apartments for this site again, to see how many new
	# apartments were added.
	num_apartments_new = Apartment.objects.filter(craigslist_site=site.id).count()
	
	# Calculate the number of apartments that were added.
	num_apartments = num_apartments_new - num_apartments_old
	if num_apartments > 0:
		site.last_collection_date = datetime.now()
		site.save()
	
	# Get the apartments that match the current search filter.
	apartments, errors = get_apartments_from_search(site, request.GET)
	
	# Set up the context (i.e. a dictionary mapping template variable names to
	# Python objects)
	context = Context({
		'site': site,
		'apartments': apartments,
		'num_apartments': num_apartments,
		'errors': errors,
	})
	
	# Render the page.
	return render_to_response('apartmenthunt/search.html', context)
