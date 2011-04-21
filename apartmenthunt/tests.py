import unittest
from datetime import datetime
from apartmenthunt.models import CraigslistSite, Apartment, get_apartments_from_search
from crawler import extract_ad_information, get_date_and_time

class CraigslistSiteTest(unittest.TestCase):
	def setUp(self):
		self.chambana = CraigslistSite.objects.create(
			site_name="Champaign-Urbana",
			site_subdomain="chambana",
			last_collection_date=datetime.now())
		self.chambana.save()
	def test_init(self):
		self.assertEqual(self.chambana.site_name, "Champaign-Urbana")
		self.assertEqual(self.chambana.site_subdomain, "chambana")

class ApartmentTest(unittest.TestCase):
	def setUp(self):
		f = open('apartment.txt', 'r')
		page_content = f.read()
		f.close()
		self.myapt = Apartment.objects.create(
			craigslist_site=1,
			listing_number=123,
			price=540,
			num_bedrooms=1,
			title="Spacious apartment near Siebel Center for Summer 2011!",
			title_address="1002 W Clark St",
			full_ad_text=page_content)
		self.myapt.save()
		site = CraigslistSite.objects.get(pk=1)
		extract_ad_information(site)
	def test_init(self):
		self.assertEqual(self.myapt.craigslist_site_id, 1)
		self.assertEqual(self.myapt.listing_number, 123)
		self.assertEqual(self.myapt.information_extracted, 1)
		# self.assertEqual(self.myapt.listing_datetime, get_date_and_time())
		self.assertEqual(self.myapt.price, 540)
		self.assertEqual(self.myapt.num_bedrooms, 1)
		self.assertEqual(self.myapt.num_bathrooms, 1)
		self.assertEqual(self.myapt.title, "Spacious apartment near Siebel Center for Summer 2011!")
		self.assertEqual(self.myapt.title_address, "1002 W Clark St")
		self.assertEqual(self.myapt.street_address, "1002 W Clark St & Clark & Gregory")
		self.assertEqual(self.myapt.city, "URBANA")
		self.assertEqual(self.myapt.state, "Illinois")
		self.assertEqual(self.myapt.cats_allowed, 0)
		self.assertEqual(self.myapt.dogs_allowed, 0)
