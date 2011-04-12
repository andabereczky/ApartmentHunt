from django.http import HttpResponse
from django.template import Context, loader
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response, get_object_or_404
from apartmenthunt.models import CraigslistSite, Apartment
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

def datacollection(request, craigslist_site_id):
	
	# Get the specified Craigslist site from the database.
	site = get_object_or_404(CraigslistSite, pk=craigslist_site_id)
	
	# Delete all old apartments in the database.
	# Apartment.objects.filter(craigslist_site=craigslist_site_id).delete()
	
	# Get the site again from the database.
	# site = get_object_or_404(CraigslistSite, pk=craigslist_site_id)
	
	# Download new data from Craigslist.
	crawler.crawl(site)
	
	# Get the site again from the database.
	site = get_object_or_404(CraigslistSite, pk=craigslist_site_id)
	num_apartments = Apartment.objects.filter(craigslist_site=craigslist_site_id).count()
	
	# Set up the context (i.e. a dictionary mapping template variable names to
	# Python objects)
	context = Context({
		'site': site,
		'num_apartments': num_apartments,
	})
	
	
	# Render the page.
	return render_to_response('apartmenthunt/datacollection.html', context)

def search(request, craigslist_site_id):
	
	# Get the specified Craigslist site from the database.
	site = get_object_or_404(CraigslistSite, pk=craigslist_site_id)
	
	# Set up the context (i.e. a dictionary mapping template variable names to
	# Python objects)
	context = Context({
		'site': site,
	})
	
	# Render the page.
	return render_to_response('apartmenthunt/search.html', context)
