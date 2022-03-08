from scraper.web_scraper import Scraper
import unittest
# from selenium import webdriver


class UploaderTest(unittest.TestCase):

    def test_open_retrieved_url_list(self):
        scr = Scraper()
        list_of_urls = scr.open_retrieved_url_list()
        self.assertIsInstance(list_of_urls, list)


if __name__ == '__main__':
    unittest.main()
