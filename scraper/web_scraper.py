from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import numpy as np
import time
import datetime
import os
import json
import urllib
import urllib.request
import urllib.error
from uuid import uuid4


class Scraper:
    def __init__(self):
        s = Service(ChromeDriverManager().install())
        self.chrome_options = Options()
        self.chrome_options.headless = True
        self.driver = webdriver.Chrome(service=s, options=self.chrome_options)
        self.driver.find_elements()

    def scrape_dates(self, links: list):
        for link in links:
            self.driver.get(link)
            time.sleep(2)
            print(f'Accessed {link}')
            if self.__if_event(link):
                print(f'No Event on {link}')
                continue
            card_races = self.get_card_races()
            self.scrape_page(link)
            for race_link in card_races:
                while True:
                    self.driver.get(race_link)
                    print(f'Accessed {race_link}')
                    time.sleep(2)
                    if not self.__if_event(race_link):
                        break
                    print(f'No Event loaded {race_link}')
                self.scrape_page(race_link)
        return

    def scrape_page(self, link):
        scraped_json = {'uuid': str(uuid4())}
        scraped_json.update(self.generate_id())
        scraped_json.update(self.race_dict())
        scraped_json['image_link'] = self.get_image_link()
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

    def generate_id(self):
        date = self.driver.find_element(
            By.XPATH,
            '/html/body/div/div[3]/p[1]/span[1]'
        ).text.split('  ')[1].replace('/', '-')
        race_number = self.driver.find_element(
            By.XPATH,
            '/html/body/div/div[4]/table/thead/tr/td[1]'
        ).text.split(' ')[1]
        id = f'{date}-{race_number}'
        race_dict = {'id': id, 'date': date, 'race_number': race_number}
        return race_dict

    def get_card_races(self):
        races = self.driver.find_elements(
            By.XPATH,
            '/html/body/div/div[2]/table/tbody/tr/td[position()<last()]/a'
        )
        links = [race.get_attribute('href') for race in races]
        return links

    def race_dict(self):
        data = self.get_race_data()
        data_dict = {'class': data[3].split(' - ')[0],
                     'length': data[3].split(' - ')[1],
                     'going': data[5],
                     'course': data[8],
                     'prize': data[9],
                     'pace': f'{data[-3]}/{data[-2]}/{data[-1]}'}
        return data_dict

    def get_race_data(self):
        data = self.driver.find_elements(
            By.XPATH,
            '/html/body/div/div[4]/table/tbody/tr/td'
        )
        data_text = [x.text for x in data]
        return data_text

    def runner_dict(self):
        table = self.get_runner_table()
        dict_runners = {'place': table[0],
                        'number': table[1],
                        'name': table[2],
                        'jockey': table[3],
                        'trainer': table[4],
                        'actual_weight': table[5],
                        'declared+weight': table[6],
                        'draw': table[7],
                        'length_behind_winner': table[8],
                        'running_positions': table[9],
                        'finish_time': table[10],
                        'win_odds': table[11],
                        'links': self.get_runner_links()}
        return dict_runners

    def get_runner_table(self):
        table = self.driver.find_elements(
            By.XPATH,
            '//table/tbody[@class="f_fs12"]/tr'
        )
        table = [self.get_runner(x) for x in table]
        return np.array(table).T.tolist()

    def get_runner(self, row):
        runner = row.find_elements_by_xpath('.//td')
        return [x.text for x in runner]

    def get_runner_links(self):
        runners = self.driver.find_elements(
            By.XPATH,
            '//table/tbody[@class="f_fs12"]/tr/td[3]/a'
        )
        links = [horse.get_attribute('href') for horse in runners]
        return links

    def get_image_link(self):
        img_link = self.driver.find_element(
            By.XPATH,
            '/html/body/div/div[6]/div[2]/div[1]/div/a/img'
        ).get_attribute('src')
        i = list(img_link)
        i[-5] = 'L'
        return ''.join(i)

    def __if_event(self, link):
        event = self.driver.find_elements(
            By.XPATH,
            '//div[@id="errorContainer"]'
        )
        abandoned = self.driver.current_url != link
        print(self.driver.current_url)
        return (bool(event) or bool(abandoned))

    def __create_date_list(self, days: int):
        start = datetime.datetime.today() - datetime.timedelta(days=1)
        return [start - datetime.timedelta(days=x) for x in range(days)]

    def __save_data(self, data: dict) -> None:
        folder = os.path.join('Web-Scraping-Data-Pipeline',
                              'raw_data', data['id'])
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(os.path.join(folder, 'data.json'), 'w') as f:
            json.dump(data, f, indent=4)
        self.__save_image(data['image_link'], data['id'])

    def __save_image(self, link, id):
        folder = os.path.join('Web-Scraping-Data-Pipeline',
                              'raw_data', id)
        for tries in range(3):
            try:
                self.driver.get(link)
                time.sleep(3)
                img = self.driver.find_element(
                    By.XPATH, '/html/body/img').get_attribute('src')
                urllib.request.urlretrieve(img, os.path.join(folder, '1.jpg'))
                break
            except urllib.error.URLError:
                print('URL error occured: ', tries)
        print(f'Saved image {id}')
