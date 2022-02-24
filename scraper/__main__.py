from web_scraper import Scraper
# import uploader
import configparser
import os


if __name__ == '__main__':
    config = configparser.ConfigParser()
    f = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '../config.ini')
    config.read(f)
#     uploader.upload_to_rds_by_id('20-02-2022-1', config['RDS'])
    num_dates = 3
    scr = Scraper()
    scr.scrape_dates(scr.create_date_links(days=num_dates))
