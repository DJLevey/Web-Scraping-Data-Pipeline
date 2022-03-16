from web_scraper import Scraper
import configparser
import os

if __name__ == '__main__':
    config = configparser.ConfigParser()
    f = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '../config.ini')
    config.read(f)
    try:
        num_dates = int(os.getenv('HISTORIC_DATES', default=1))
    except TypeError:
        num_dates = 1
    scr = Scraper()
    scr.scrape_dates(
            scr.create_date_links(days=num_dates),
            config['RDS'],
            config['S3']['bucket']
            )
