from scraper.web_scraper import Scraper
import unittest
import configparser
import os
from selenium import webdriver


class ScraperTest(unittest.TestCase):

    def test_scraper_class(self):
        scr = Scraper()
        self.assertIsInstance(scr.driver, webdriver.Chrome)

    def test_create_date_links(self):
        scr = Scraper()
        dates = scr.create_date_links()
        self.assertIsInstance(dates, list)
        self.assertTrue(len(dates) == 1)
        self.assertIsInstance(dates[0], str)
        dates = scr.create_date_links(5)
        self.assertTrue(len(dates) == 5)
        with self.assertRaises(TypeError):
            dates = scr.create_date_links('f')

    def test_scrape_dates(self):
        config = configparser.ConfigParser()
        f = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '../config.ini')
        config.read(f)
        scr = Scraper()
        with self.assertRaises(ValueError):
            scr.scrape_dates(
                ['bad_url.com'],
                config['RDS'],
                config['S3']['bucket']
            )


if __name__ == '__main__':
    unittest.main()
