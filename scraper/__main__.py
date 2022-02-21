from web_scraper import Scraper

if __name__ == '__main__':
    bucket = 'aicorebucket828'
    num_dates = 3
    scr = Scraper()
    scr.scrape_dates(scr.create_date_links(days=num_dates))
