from scraper.uploader import get_no_event_urls, get_retrieved_urls
import unittest
import configparser
import os


class UploaderTest(unittest.TestCase):

    def test_open_retrieved_url_list(self):
        config = configparser.ConfigParser()
        f = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '../config.ini')
        config.read(f)
        list_of_urls = get_retrieved_urls(config['RDS'])
        self.assertIsInstance(list_of_urls, list)

    def test_get_no_event_urls(self):
        config = configparser.ConfigParser()
        f = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '../config.ini')
        config.read(f)
        list_of_urls = get_no_event_urls(config['RDS'])
        self.assertIsInstance(list_of_urls, list)


if __name__ == '__main__':
    unittest.main()
