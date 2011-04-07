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
	
	# Extract the URLs of each individual ad.
	listing_numbers = extract_ad_urls(main_page_content)
	
	# Download each ad and save it in the database.
	download_and_save_pages(site, listing_numbers)

def extract_ad_urls(page_content):
	'''Extracts the individual URLs to ads from the Craigslist main search
	page.'''
	
	# Create the regular expression used to extract the urls.
	pattern = '<p><a href="http://chambana\.craigslist\.org/apa/(?P<listing_number>\d+)\.html">'
	pattern += '(((\$(?P<price>\d+) / (?P<num_bedrooms>\d+)br)|(\$(?P<price1>\d+))|((?P<num_bedrooms1>\d+)br)) - )'
	pattern += '(?P<title>.*)</a> - '
	pattern += '<font size="-1"> \((?P<address>.*)\)</font>'
	regex = re.compile(pattern)
	
	# Extract the URLs
	listing_numbers = []
	for match in regex.finditer(page_content):
		listing_numbers.append(match.group('listing_number'))
	return listing_numbers

def download_and_save_pages(site, listing_numbers):
	'''Downloads the web pages with the given listing numbers from the given
	Craigslist site.'''
	
	for listing_number in listing_numbers:
		url = 'http://chambana.craigslist.org/apa/%s.html' % listing_number
		print 'Downloading page %s...' % url
		page_reader = urlopen(url)
		try:
			page_content = page_reader.read().encode('ascii', 'ignore')
			new_apt = Apartment(craigslist_site=site, full_ad_text=page_content)
			new_apt.save()
			print 'done.'
		except UnicodeDecodeError:
			print 'failed due to UnicodeDecodeError.'
