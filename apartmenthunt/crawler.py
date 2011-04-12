from urllib import urlopen
import re
from apartmenthunt.models import CraigslistSite, Apartment

def crawl(site):
	'''Crawls the given Craigslist site.'''
	
	# Construct the URL of the site.
	url = "http://" + site.site_subdomain + ".craigslist.org/apa/"
	
	# Download the main page of the site.
	page_reader = urlopen(url)
	main_page_content = page_reader.read()
	
	# Download each individual ad.
	# download_ads(site, main_page_content)
	
	# Extract information from ads
	extract_ad_information(site)

def download_ads(site, main_page_content):
	'''
	Extracts the individual URLs to ads from the Craigslist main search page,
	extract preliminary information about each ad from the main search page,
	save all this information in the database.
	'''
	
	# Create the regular expression used to extract the urls and the preliminary
	# information.
	pattern = '<p><a href="http://chambana\.craigslist\.org/apa/(?P<listing_number>\d+)\.html">'
	pattern += '(((\$(?P<price1>\d+) / (?P<num_bedrooms1>\d+)br)|(\$(?P<price2>\d+))|((?P<num_bedrooms2>\d+)br)) - )'
	pattern += '(?P<title>.*)</a> - '
	pattern += '<font size="-1"> \((?P<address>.*)\)</font>'
	regex = re.compile(pattern)
	
	# Download the HTML code of each ad and save it in the database together
	# with the information extracted from the main page.
	for match in regex.finditer(main_page_content):
		
		# Get the preliminary information.
		listing_number = match.group('listing_number')
		price = match.group('price1')
		if price == None:
			price = match.group('price2')
		num_bedrooms = match.group('num_bedrooms1')
		if num_bedrooms == None:
			num_bedrooms = match.group('num_bedrooms2')
		title = match.group('title')
		address = match.group('address')
		
		# Build the ad page URL
		url = 'http://chambana.craigslist.org/apa/%s.html' % listing_number
		
		# Download the page
		print 'Downloading page %s...' % url
		page_reader = urlopen(url)
		try:
			page_content = page_reader.read().encode('ascii', 'ignore')
		except UnicodeDecodeError:
			print 'failed due to UnicodeDecodeError.'
			continue
		
		# Save the page to the database
		new_apt = Apartment(
			craigslist_site=site,
			listing_number=listing_number,
			price=price,
			num_bedrooms=num_bedrooms,
			title=title,
			address=address,
			full_ad_text=page_content)
		new_apt.save()
		print 'done.'

def extract_ad_information(site):
	# TODO: implement
	pass