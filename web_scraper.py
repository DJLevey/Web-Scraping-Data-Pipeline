from selenium import webdriver
# import pandas as pd
import time


class Scraper:
    def __init__(self):
        self.driver = webdriver.Chrome()
        URL = ('https://racing.hkjc.com/racing/information/'
               'English/Racing/LocalResults.aspx?RaceDate=2022/02/06')
        self.driver.get(URL)
        time.sleep(2)

    def get_runners(self):
        runners = self.driver.find_elements_by_xpath(
            '//table/tbody[@class="f_fs12"]/tr/td[3]'
        )
        for horse in runners:
            a_tag = horse.find_element_by_tag_name('a')
            link = a_tag.get_attribute('href')
            print(horse.text[:-6], '  ', link)


if __name__ == '__main__':
    scr = Scraper()
    scr.get_runners()
