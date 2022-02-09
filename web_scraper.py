from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import datetime


class Scraper:
    def __init__(self, URL):
        self.driver = webdriver.Chrome()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(URL)
        time.sleep(2)

    def date_list(self, days):
        today = datetime.datetime.today()
        return [today - datetime.timedelta(days=x) for x in range(days)]

    def get_runners(self):
        runners = self.driver.find_elements_by_xpath(
            '//table/tbody[@class="f_fs12"]/tr/td[3]'
        )
        links = []
        for horse in runners:
            a_tag = horse.find_element_by_tag_name('a')
            link = a_tag.get_attribute('href')
            links.append(link)
        return links


if __name__ == '__main__':
    URL = ('https://racing.hkjc.com/racing/information/'
           'English/Racing/LocalResults.aspx?RaceDate=2022/02/06')
    scr = Scraper(URL)
    print(scr.date_list(10))
    scr.get_runners()
