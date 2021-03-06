from sqlalchemy.engine.base import Engine
import unittest
import configparser
import sys
import os
sys.path.append('..')
sys.path.append('../scraper')
from scraper.uploader import (  # noqa: E402
                        get_no_event_urls,
                        get_retrieved_urls,
                        _connect_to_rds
                        )


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

    def test__connect_to_rds(self):
        config = configparser.ConfigParser()
        f = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '../config.ini')
        config.read(f)
        engine = _connect_to_rds(config['RDS'])
        self.assertIsInstance(engine, Engine)
        con = engine.connect()
        self.assertIsInstance(con.nano)


if __name__ == '__main__':
    unittest.main()
