from web_scraper import Scraper
import os

if __name__ == '__main__':
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    scr = Scraper()
    scr.scrape_dates(scr.create_date_links(days=2))
