from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import datetime


class Scraper:
    def __init__(self, URL):
        chrome_options = Options().add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(URL)
        time.sleep(2)

    def date_list(self, days):
        today = datetime.datetime.today()
        return [today - datetime.timedelta(days=x) for x in range(days)]

    def create_date_links(self, days):
        base_url = ('https://racing.hkjc.com/racing/information/'
                    'English/Racing/LocalResults.aspx?RaceDate=')
        date_links = []
        dates = self.date_list(days)
        for date in dates:
            year = str(date.year)
            month = str(date.month).zfill(2)
            day = str(date.day).zfill(2)
            link = f'{base_url}{year}/{month}/{day}'
            date_links.append(link)
        return date_links

    def get_card_races(self):
        races = self.driver.find_elements_by_xpath(
            '//table[@class="f_fs12 f_fr js_racecard"]/tbody/tr/td/a'
        )
        links = [race.get_attribute('href') for race in races]
        return links

    def get_runners(self):
        runners = self.driver.find_elements_by_xpath(
            '//table/tbody[@class="f_fs12"]/tr/td[3]/a'
        )
        links = [horse.get_attribute('href') for horse in runners]
        return links

    def navigate_pages(self):
        links_by_date = self.create_date_links(5)
        horse_links = {}
        for link in links_by_date:
            self.driver.get(link)
            time.sleep(3)
            card_races = self.get_card_races()
            horse_links.update(self.get_runners())
            for race_link in card_races:
                self.driver.get(race_link)
                time.sleep(2)
                horse_links.update(self.get_runners())
        return True


if __name__ == '__main__':
    URL = ('https://racing.hkjc.com/racing/information/'
           'English/Racing/LocalResults.aspx?RaceDate=2022/02/06')
    scr = Scraper(URL)
