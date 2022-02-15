from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import numpy as np
import time
import datetime
import os
import json
import urllib
import urllib.request
from uuid import uuid4


class Scraper:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.headless = True
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.horse_links = set()

    def scrape_dates(self, links: list):
        for link in links:
            self.driver.get(link)
            time.sleep(3)
            print(f'Accessed {link}')
            if self.if_event():
                print(f'No Event on {link}')
                continue
            card_races = self.get_card_races()
            self.scrape_page(link)
            for race_link in card_races:
                self.scrape_page(race_link)
        return

    def scrape_page(self, link):
        scraped_json = {'uuid': str(uuid4())}
        if self.driver.current_url != link:
            self.driver.get(link)
            print(f'Accessed {link}')
            time.sleep(3)
        self.scrape_race_data()
        scraped_json['image_link'] = self.get_image_link()
        scraped_json['id'] = scraped_json['image_link'][-16:-6]
        scraped_json['runners'] = self.runner_dict()
        self.__save_data(scraped_json)

    def create_date_links(self, days):
        base_url = ('https://racing.hkjc.com/racing/information/'
                    'English/Racing/LocalResults.aspx?RaceDate=')
        dates = self.__create_date_list(days)
        date_links = [f'{base_url}{str(date.year)}/'
                      f'{str(date.month).zfill(2)}/'
                      f'{str(date.day).zfill(2)}' for date in dates]
        return date_links

    def get_card_races(self):
        races = self.driver.find_elements_by_xpath(
            '/html/body/div/div[2]/table/tbody/tr/td[position()<last()]/a'
        )
        links = [race.get_attribute('href') for race in races]
        return links

    def scrape_race_data(self):
        data = self.driver.find_elements_by_xpath(
            '/html/body/div/div[4]/table/tbody/tr/td'
        )
        for i in data:
            print(i.text)
        return

    def runner_dict(self):
        table = self.get_runner_table()
        dict_runners = {'Place': table[0],
                        'Number': table[1],
                        'Name': table[2],
                        'Jockey': table[3],
                        'Trainer': table[4],
                        'Actual Weight': table[5],
                        'Declared Weight': table[6],
                        'Draw': table[7],
                        'Length Behind Winner': table[8],
                        'Running Positions': table[9],
                        'Finish Time': table[10],
                        'Win Odds': table[11],
                        'Links': self.get_runner_links()}
        return dict_runners

    def get_runner_table(self):
        table = self.driver.find_elements_by_xpath(
            '//table/tbody[@class="f_fs12"]/tr'
        )
        table = [self.get_runner(x) for x in table]
        return np.array(table).T.tolist()

    def get_runner(self, row):
        runner = row.find_elements_by_xpath('.//td')
        return [x.text for x in runner]

    def get_runner_links(self):
        runners = self.driver.find_elements_by_xpath(
            '//table/tbody[@class="f_fs12"]/tr/td[3]/a'
        )
        links = [horse.get_attribute('href') for horse in runners]
        return links

    def get_image_link(self):
        img_link = self.driver.find_element_by_xpath(
            '/html/body/div/div[6]/div[2]/div[1]/div/a/img'
        ).get_attribute('src')
        i = list(img_link)
        i[-5] = 'L'
        return ''.join(i)

    def if_event(self):
        event = self.driver.find_elements_by_xpath(
            '//div[@id="errorContainer"]'
        )
        return bool(event)

    def __create_date_list(self, days: int):
        today = datetime.datetime.today()
        return [today - datetime.timedelta(days=x) for x in range(days)]

    def __save_data(self, data: dict):
        folder = os.path.join('Web-Scraping-Data-Pipeline',
                              'raw_data', data['id'])
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(os.path.join(folder, 'data.json'), 'w') as f:
            json.dump(data, f, indent=4)
        self.__save_image(data['image_link'], data['id'])
        return

    def __save_image(self, link, id):
        folder = os.path.join('Web-Scraping-Data-Pipeline',
                              'raw_data', id)
        self.driver.get(link)
        time.sleep(2)
        img = self.driver.find_element_by_xpath(
            '/html/body/img'
        ).get_attribute('src')
        urllib.request.urlretrieve(img, os.path.join(folder, '1.jpg'))
        print(f'Saved image {id}')
        return


if __name__ == '__main__':
    URL = ('https://racing.hkjc.com/racing/information/English/Racing'
           '/LocalResults.aspx?RaceDate=2022/02/12&Racecourse=ST&RaceNo=2')
    scr = Scraper()
    scr.scrape_dates(scr.create_date_links(4))
