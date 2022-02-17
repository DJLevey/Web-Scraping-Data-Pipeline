from web_scraper import Scraper

if __name__ == '__main__':
    scr = Scraper()
    scr.scrape_dates(scr.create_date_links(1))
