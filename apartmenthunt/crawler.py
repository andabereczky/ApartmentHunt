from urllib import urlopen
from decimal import Decimal
from datetime import datetime
import re
from django.shortcuts import get_object_or_404
from apartmenthunt.models import CraigslistSite, Apartment

# Taken from http://www.usps.com/ncsc/lookups/abbreviations.html
date_and_time_pattern = 'Date: (?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2}), (?P<hours>( |[0-9])[0-9]):(?P<minutes>[0-9]{2})(?P<am_or_pm>AM|PM) (EDT|EST|CDT|CST|MDT|MST|PDT|PST)'
number = '[0-9]+[A-Za-z]*'
street = '(([A-Z]|[0-9]+)[a-z]*[.]?[ ]?){1,2}'
street_suffix = '(%s)' % '|'.join(('ALLEE','ALLEY','ALLY','ALY','AV','AVE','AVEN','AVENU','AVENUE','AVN','AVNUE','BLVD','BOUL','BOULEVARD','BOULV',
    'BYP','BYPA','BYPAS','BYPASS','BYPS','CIR','CIRC','CIRCL','CIRCLE','COURT','COVE','CRCL','CRCLE','CRECENT','CRES','CRESCENT','CRESENT','CRSCNT',
    'CRSENT','CRSNT','CRT','CT','CV','DR','DRIV','DRIVE','DRV','EXP','EXPR','EXPRESS','EXPRESSWAY','EXPW','EXPY','EXT','EXTENSION','EXTN','EXTNSN',
    'FREEWAY','FREEWY','FRWAY','FRWY','FWY','GREEN','GRN','HIGHWAY','HIGHWY','HIWAY','HIWY','HWAY','HWY','LA','LANE','LANES','LN','LOOP','LOOPS',
    'MALL','MANOR','MNR','PARKWAY','PARKWY','PATH','PATHS','PIKE','PIKES','PKWAY','PKWY','PKY','PL','PLACE','PLAZA','PLZ','PLZA','RD','ROAD','ROUTE',
    'RTE','SPUR','SQ','SQR','SQRE','SQU','SQUARE','ST','STR','STREET','STRT','TER','TERR','TERRACE','THROUGHWAY','TPK','TPKE','TR','TRACE','TRACES',
    'TRACK','TRACKS','TRAIL','TRAILS','TRAK','TRCE','TRK','TRKS','TRL','TRLS','TRNPK','TRPK','TRWY','TURNPIKE','TURNPK','VDCT','VIA','VIADCT',
    'VIADUCT','WALK','WAY','WY'))
city = '([A-Z][a-z]+[.]?[ ]?){3,}'
state = '(%s)' % '|'.join(('ALABAMA','AL','ALASKA','AK','AMERICAN SAMOA','AS','ARIZONA','AZ','ARKANSAS','AR','CALIFORNIA','CA','COLORADO','CO',
    'CONNECTICUT','CT','DELAWARE','DE','DISTRICT OF COLUMBIA','DC','FLORIDA','FL','GEORGIA','GA',
    'HAWAII','HI','IDAHO','ID','ILLINOIS','IL','INDIANA','IN','IOWA','IA','KANSAS','KS','KENTUCKY','KY','LOUISIANA','LA','MAINE','ME',
    'MARYLAND','MD','MASSACHUSETTS','MA','MICHIGAN','MI','MINNESOTA','MN','MISSISSIPPI','MS','MISSOURI','MO','MONTANA','MT',
    'NEBRASKA','NE','NEVADA','NV','NEW HAMPSHIRE','NH','NEW JERSEY','NJ','NEW MEXICO','NM','NEW YORK','NY','NORTH CAROLINA','NC','NORTH DAKOTA','ND',
    'OHIO','OH','OKLAHOMA','OK','OREGON','OR','PALAU','PW','PENNSYLVANIA','PA','PUERTO RICO','PR','RHODE ISLAND','RI',
    'SOUTH CAROLINA','SC','SOUTH DAKOTA','SD','TENNESSEE','TN','TEXAS','TX','UTAH','UT','VERMONT','VT','VIRGIN ISLANDS','VI','VIRGINIA','VA',
    'WASHINGTON','WA','WEST VIRGINIA','WV','WISCONSIN','WI','WYOMING','WY'))
street_address_pattern = '(?P<street_address>%s %s( %s)?[.]?)' % (number, street, street_suffix)
city_state_pattern = '((?P<city>%s),[ ]?(?P<state>%s))' % (city, state)
cltag_xstreet0_pattern = '<!-- CLTAG xstreet0=(?P<xstreet0>.*?) -->'
cltag_xstreet1_pattern = '<!-- CLTAG xstreet1=(?P<xstreet1>.*?) -->'
cltag_city_pattern = '<!-- CLTAG city=(?P<city>.*?) -->'
cltag_state_pattern = '<!-- CLTAG region=(?P<state>.*?) -->'
cltag_dogs_pattern = '<!-- CLTAG dogsAreOK=on -->'
cltag_cats_pattern = '<!-- CLTAG catsAreOK=on -->'

# Needed only if this information is not extracted from the main search page.
# cltag_geographic_area = '<!-- CLTAG GeographicArea=(?P<geographic_area>.*?) -->'

def crawl(site):
	'''Crawls the given Craigslist site.'''
	
	# Construct the URL of the site.
	url = "http://" + site.site_subdomain + ".craigslist.org/apa/"
	
	# Download the main page of the site.
	page_reader = urlopen(url)
	main_page_content = page_reader.read()
	
	# Download each individual ad.
	download_ads(site, main_page_content)
	
	# Comment this out for release
	apartments = Apartment.objects.filter(craigslist_site=site.id)
	for apartment in apartments:
		apartment.information_extracted = False
		apartment.save()
	
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
		
		# Get the listing number and check if this listing has already been
		# added to the database.
		listing_number = match.group('listing_number')
		try:
			Apartment.objects.get(listing_number=listing_number)
			break
		except Apartment.DoesNotExist:
			pass
		
		# Get the preliminary information.
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
			title_address=address,
			full_ad_text=page_content)
		new_apt.save()
		print 'done.'

def extract_ad_information(site):
	
	# Get the apartments belonging to the given site.
	apartments = Apartment.objects.filter(craigslist_site=site.id)
	
	# Compile all needed regular expressions.
	date_and_time_regex = re.compile(date_and_time_pattern)
	pattern = '\$(?P<price>\d+)' # price
	price_regex = re.compile(pattern)
	pattern = '((?P<num_bedrooms1>\d+) ?br)|((?P<num_bedrooms2>\d+) bedroom(s)?)' # number of bedrooms
	num_bedrooms_regex = re.compile(pattern, re.IGNORECASE)
	pattern = '((?P<num_bathrooms1>(\d+)\.?(\d+)?) ?ba)|((?P<num_bathrooms2>(\d+)\.?(\d+)?) bathroom(s)?)' # number of bathrooms
	num_bathrooms_regex = re.compile(pattern, re.IGNORECASE)
	street_address_regex = re.compile(street_address_pattern, re.IGNORECASE) # street address
	city_state_regex = re.compile(city_state_pattern, re.IGNORECASE) # city and state
	cltag_xstreet0_regex = re.compile(cltag_xstreet0_pattern, re.IGNORECASE) # street location
	cltag_xstreet1_regex = re.compile(cltag_xstreet1_pattern, re.IGNORECASE) # closest intersection
	cltag_city_regex = re.compile(cltag_city_pattern, re.IGNORECASE) # city
	cltag_state_regex = re.compile(cltag_state_pattern, re.IGNORECASE) # state
	cltag_dogs_regex = re.compile(cltag_dogs_pattern) # are dogs allowed?
	cltag_cats_regex = re.compile(cltag_cats_pattern) # are cats allowed?
	
	# Loop through all apartments.
	num = 0
	for apartment in apartments:
		
		if apartment.information_extracted:
			continue
		
		print 'Apartment #%d:' % apartment.id
		updated = False
		
		# Strip HTML tags from the ad page.
		ad_text_no_html = remove_html_tags(apartment.full_ad_text)
		
		# Extract listing date and time.
		date_and_time_match = date_and_time_regex.search(ad_text_no_html)
		if date_and_time_match:
			date_and_time = get_date_and_time(
				int(date_and_time_match.group('year')),
				int(date_and_time_match.group('month')),
				int(date_and_time_match.group('day')),
				int(date_and_time_match.group('hours')),
				int(date_and_time_match.group('minutes')),
				date_and_time_match.group('am_or_pm'))
			apartment.listing_datetime = date_and_time
			updated = True
		
		# Extract price.
		price_match = price_regex.search(ad_text_no_html)
		if price_match:
			new_price = price_match.group('price')
			if new_price:
				new_price = int(new_price)
				if apartment.price:
					if apartment.price != new_price:
						print '  Price conflict: %d != %d' % (apartment.price, new_price)
				else:
					apartment.price = new_price
					updated = True
		
		# Extract number of bedrooms.
		num_bedrooms_match = num_bedrooms_regex.search(ad_text_no_html)
		if num_bedrooms_match:
			new_num_bedrooms1 = num_bedrooms_match.group('num_bedrooms1')
			new_num_bedrooms2 = num_bedrooms_match.group('num_bedrooms2')
			if new_num_bedrooms1:
				new_num_bedrooms1 = int(new_num_bedrooms1)
				if apartment.num_bedrooms:
					if apartment.num_bedrooms != new_num_bedrooms1:
						print '  Number of bedrooms conflict: %d != %d' % (apartment.num_bedrooms, new_num_bedrooms1)
				else:
					apartment.num_bedrooms = new_num_bedrooms1
					updated = True
			if new_num_bedrooms2:
				new_num_bedrooms2 = int(new_num_bedrooms2)
				if apartment.num_bedrooms:
					if apartment.num_bedrooms != new_num_bedrooms2:
						print '  Number of bedrooms conflict: %d != %d' % (apartment.num_bedrooms, new_num_bedrooms2)
				else:
					apartment.num_bedrooms = new_num_bedrooms2
					updated = True
		
		# Extract number of bathrooms.
		num_bathrooms_match = num_bathrooms_regex.search(ad_text_no_html)
		if num_bathrooms_match:
			new_num_bathrooms1 = num_bathrooms_match.group('num_bathrooms1')
			new_num_bathrooms2 = num_bathrooms_match.group('num_bathrooms2')
			if new_num_bathrooms1:
				new_num_bathrooms1 = Decimal(new_num_bathrooms1)
				if apartment.num_bathrooms:
					if apartment.num_bathrooms != new_num_bathrooms1:
						print '  Number of bathrooms conflict: %d != %d' % (apartment.num_bathrooms, new_num_bathrooms1)
				else:
					apartment.num_bathrooms = new_num_bathrooms1
					updated = True
			if new_num_bathrooms2:
				new_num_bathrooms2 = Decimal(new_num_bathrooms2)
				if apartment.num_bathrooms:
					if apartment.num_bathrooms != new_num_bathrooms2:
						print '  Number of bathrooms conflict: %d != %d' % (apartment.num_bathrooms, new_num_bathrooms2)
				else:
					apartment.num_bathrooms = new_num_bathrooms2
					updated = True
		
		# Extract address from title.
		street_address_match = street_address_regex.search(apartment.title_address)
		city_state_match = city_state_regex.search(apartment.title_address)
		if street_address_match:
			apartment.street_address = street_address_match.group('street_address')
			updated = True
			num += 1
		if city_state_match:
			apartment.city = city_state_match.group('city')
			apartment.state = city_state_match.group('state')
			updated = True
		
		# Extract street address from ad content.
		if not apartment.street_address:
			cltag_xstreet0_match = cltag_xstreet0_regex.search(apartment.full_ad_text)
			if cltag_xstreet0_match:
				apartment.street_address = cltag_xstreet0_match.group('xstreet0')
				updated = True
				num += 1
		if not apartment.street_address:
			cltag_xstreet1_match = cltag_xstreet1_regex.search(apartment.full_ad_text)
			if cltag_xstreet1_match:
				apartment.street_address = cltag_xstreet1_match.group('xstreet1')
				updated = True
				num += 1
		
		# Extract city and state from ad content.
		cltag_city_match = cltag_city_regex.search(apartment.full_ad_text)
		if cltag_city_match:
			city = cltag_city_match.group('city')
			if apartment.city and apartment.city.lower() != city.lower():
				print '  City conflict: %s != %s' % (apartment.city, city)
			apartment.city = city
			updated = True
		cltag_state_match = cltag_state_regex.search(apartment.full_ad_text)
		if cltag_state_match:
			state = cltag_state_match.group('state')
			if apartment.state and apartment.state.lower() != state.lower():
				print '  State conflict: %s != %s' % (apartment.state, state)
			apartment.state = state
			updated = True
		
		# Extract pets information.
		cltag_dogs_match = cltag_dogs_regex.search(apartment.full_ad_text)
		if cltag_dogs_match:
			apartment.dogs_allowed = True
			updated = True
		cltag_cats_match = cltag_cats_regex.search(apartment.full_ad_text)
		if cltag_cats_match:
			apartment.cats_allowed = True
			updated = True
		
		# Save the extracted information.
		if updated:
			apartment.save()
		
	print 'extracted %d street addresses' % num

def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def get_date_and_time(year, month, day, hours, minutes, am_or_pm):
	if am_or_pm == 'PM' and hours > 12:
		hours += 12
	return datetime(year, month, day, hours, minutes, 0)