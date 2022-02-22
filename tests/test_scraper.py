from scraper.web_scraper import Scraper
import unittest
from selenium import webdriver


class ScraperTest(unittest.TestCase):
    def test_scraper_class(self):
        scr = Scraper()
        self.assertIsInstance(scr.driver, webdriver.Chrome)

    def test_open_retrieved_url_list(self):
        scr = Scraper()
        list_of_urls = scr.open_retrieved_url_list()
        self.assertIsInstance(list_of_urls, list)

    def test_create_date_links(self):
        scr = Scraper()
        dates = scr.create_date_links()
        self.assertIsInstance(dates, list)
        self.assertTrue(len(dates) == 1)
        self.assertIsInstance(dates[0], str)
        dates = scr.create_date_links(5)
        self.assertTrue(len(dates) == 5)


if __name__ == '__main__':
    unittest.main()
