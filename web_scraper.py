from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import datetime


class Scraper:
    def __init__(self, URL):
        self.chrome_options = Options().add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.chrome_options)

    def navigate_pages(self, days):
        links_by_date = self.create_date_links(days)
        horse_links = set()
        for link in links_by_date:
            self.driver.get(link)
            time.sleep(3)
            print(f'Accessed {link}')
            if self.if_event():
                print('No Event.')
                continue
            card_races = self.get_card_races()
            horse_links = horse_links.union(self.get_runners())
            for race_link in card_races:
                self.driver.get(race_link)
                print(f'Accessed {race_link}')
                time.sleep(2)
                horse_links = horse_links.union(self.get_runners())
            print(len(horse_links))
        return True

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
            '//table[@class="f_fs12 f_fr js_racecard"]'
            '/tbody/tr/td[position()<last()]/a'
        )
        links = [race.get_attribute('href') for race in races]
        return links

    def get_runners(self):
        runners = self.driver.find_elements_by_xpath(
            '//table/tbody[@class="f_fs12"]/tr/td[3]/a'
        )
        links = {horse.get_attribute('href') for horse in runners}
        return links

    def if_event(self):
        event = self.driver.find_elements_by_xpath(
            '//div[@id="errorContainer"]'
        )
        return bool(event)


if __name__ == '__main__':
    URL = ('https://racing.hkjc.com/racing/information/'
           'English/Racing/LocalResults.aspx?RaceDate=2022/02/06')
    scr = Scraper(URL)
    scr.navigate_pages(3)
