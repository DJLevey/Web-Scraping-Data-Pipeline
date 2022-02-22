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
from uploader import upload_to_bucket_by_id

'''Hong Kong Jockey Club Web-Scraper


'''


class Scraper(object):
    '''Scraper Class

    '''

    def __init__(self):
        '''Initialises Scraper

        Parameters:
            driver (webdriver): Google Chrome webdriver.
            retrieved_urls (list): A list of URLs that has been
                previously scraped.
            raw_data_path (str): Location of data folder.
        '''
        s = Service(ChromeDriverManager().install())
        chrome_options = Options()
        chrome_options.headless = True
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=s, options=chrome_options)
        self.driver.find_elements()
        self.raw_data_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '../raw_data/')
        self.retrieved_urls = self.open_retrieved_url_list()

    def open_retrieved_url_list(self) -> list():
        '''Get list of previously scraped URLs

        Iterates through the raw_data floder andr etrieves a list of
        previously scraped URLs from the json files.

        Returns:
            list (str): A list of URLs.
        '''
        list_of_urls = []
        for x in os.listdir(self.raw_data_path):
            sub_dir = os.path.join(self.raw_data_path, x)
            if os.path.isdir(sub_dir):
                for fname in os.listdir(sub_dir):
                    print(fname)
                    if fname.endswith('.json'):
                        with open(os.path.join(sub_dir, fname), 'r') as f:
                            list_of_urls.append(json.load(f)['url'])
        print(list_of_urls)
        return list_of_urls

    def scrape_dates(self, links: list) -> None:
        '''Scrapes website for along a list of dates.

        Iterates throuch a list of urls, created from dates, and
        calles methods to scrapes them for additional races and
        data and data to be stored. The next race of the day is then
        loaded and scraped. Once all of the races on a day have been
        scraped, the next days result page will be loaded.

        Args:
            links: a list of urls to the first race of a day.
        '''
        for link in links:
            self.driver.get(link)
            time.sleep(2)
            if self._if_event(link):
                print(f'No Event on {link}')
                continue
            card_races = self.get_card_races()
            if link not in self.retrieved_urls:
                self.scrape_page()
            for race_link in card_races:
                if race_link in self.retrieved_urls:
                    print(f'Data Already Retrieved: {race_link}')
                    continue
                while True:
                    self.driver.get(race_link)
                    print(f'Accessed {race_link}')
                    time.sleep(2)
                    if not self._if_event(race_link):
                        break
                    print(f'No Event loaded {race_link}')
                self.scrape_page()
        return

    def scrape_page(self) -> None:
        '''Scrapes current webpage to a dictionary.-

        Creates a dictionary with a unique identifier and
        scrapes the page for data relevant to the race. Then
        saves them to a JSON file.
        '''
        scraped_json = {'uuid': str(uuid4())}
        scraped_json.update(self._generate_id())
        scraped_json.update(self.race_dict())
        scraped_json['image_link'] = self._get_image_link()
        scraped_json['runners'] = self.runner_dict()
        self._save_data(scraped_json)
        self._save_image(scraped_json['image_link'], scraped_json['id'])
        if upload_to_bucket_by_id(scraped_json['id']):
            print('files uploaded to bucket')

    def create_date_links(self, days=1) -> list:
        ''' Creates a list of URLs to be used by the scrape_page method

        Creates a list of dates for a range of dates, starting with the
        previous day, and uses them to create URLs to the page for the
        results of the first race on the given day. The default value
        of 1 will return a list containing a single URL to yesterdays results.

        Args:
            days (int): The number of dates to be scraped before the
            current date.

        Returns:
            list(str): The list of URLs for the first race on the given day.
        '''
        base_url = ('https://racing.hkjc.com/racing/information/'
                    'English/Racing/LocalResults.aspx?RaceDate=')
        dates = self._create_date_list(days)
        date_links = [f'{base_url}{str(date.year)}/'
                      f'{str(date.month).zfill(2)}/'
                      f'{str(date.day).zfill(2)}' for date in dates]
        return date_links

    def _generate_id(self) -> dict:
        ''' Generates a unique race ID

        Generates a human readable unique ID for each race by scraping
        the date and the race number from the current page, then returns
        a dictionary with those three keys.

        Returns:
            dict: A dictionary containing the current races ID, date,
            and race number.
        '''
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

    def get_card_races(self) -> list:
        '''Get daily races from first page.

        Searches the current page of other races taking place on that date.

        Returns:
            list(str): a list of URLs for other pages to scrape.
        '''
        races = self.driver.find_elements(
            By.XPATH,
            '/html/body/div/div[2]/table/tbody/tr/td[position()<last()]/a'
        )
        links = [race.get_attribute('href') for race in races]
        return links

    def race_dict(self) -> dict:
        '''Create dictionary from scraped date.

        Calls get_race_data and creates a dictionary for the details
        pertaining to the race.

        Returns:
            dict: Dictionart of race details.
        '''
        data = self.get_race_data()
        data_dict = {'class': data[3].split(' - ')[0],
                     'length': data[3].split(' - ')[1],
                     'going': data[5],
                     'course': data[8],
                     'prize': data[9],
                     'pace': f'{data[-3]}/{data[-2]}/{data[-1]}',
                     'url': self.driver.current_url}
        return data_dict

    def get_race_data(self) -> list:
        '''Scrape the current page for race details.

        Scrapes a table from the current page containing a list of
        details, and returns them as a list.

        Returns:
            list (str): A list of raw data, extracted from current page.
        '''
        data = self.driver.find_elements(
            By.XPATH,
            '/html/body/div/div[4]/table/tbody/tr/td'
        )
        data_text = [x.text for x in data]
        return data_text

    def runner_dict(self) -> dict:
        '''Creates a dictionary for each runner.

        Calls _get_runner_table to scrape the current page for all of the
        runners in the race, and creates a dictionary with the details
        of each runner.

        Returns:
            dict: A dictionary of runner details.
        '''
        table = self._get_runner_table()
        dict_runners = {'uuid': str(uuid4()),
                        'place': table[0],
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
                        'links': self._get_runner_links()}
        return dict_runners

    def _get_runner_table(self) -> list:
        '''Scrape the current page for the details of each runner.

        Scrapes a table from the current page containing a list of
        details, and returns them as a list.

        Returns:
            list (str): a 2-dimensional list of details for each runner.
        '''
        table = self.driver.find_elements(
            By.XPATH,
            '/html/body/div/div[5]/table/tbody/tr'
        )
        table = [self._get_runner(x) for x in table]
        return np.array(table).T.tolist()

    def _get_runner(self, row) -> list:
        '''Extract text for each runner.

        Args:
            row (WebElement): A row from the table of runners.

        Returns:
            list (str): A list of parameters for a runner.
        '''
        runner = row.find_elements(By.XPATH, './/td')
        return [x.text for x in runner]

    def _get_runner_links(self) -> list:
        ''' Get URL for each runner

        Scrapes a URL to the page for each runner and returns them
        as a list.

        Returns:
            list (str): A list of URLs to the runners of the race.
        '''
        runners = self.driver.find_elements(
            By.XPATH,
            '/html/body/div/div[5]/table/tbody/tr/td[3]/a'
        )
        links = [horse.get_attribute('href') for horse in runners]
        return links

    def _get_image_link(self) -> str:
        ''' Get link for race image.

        Retrieves the URL for the picture finish for the current page,
        and alters it to reach the larger version.

        Returns:
            str: A URL to the page containing a photograph of the race finish.
        '''
        img_link = self.driver.find_element(
            By.XPATH,
            '/html/body/div/div[6]/div[2]/div[1]/div/a/img'
        ).get_attribute('src')
        i = list(img_link)
        i[-5] = 'L'
        return ''.join(i)

    def _if_event(self, link) -> bool:
        '''Checks the current page for data to scrape

        Searches the current page for errorContainers, indicating that
        there is no race on this date, and compares current URL to
        intended URL incase of redirection.

        Args:
            link (str): Intended URL to compare to current.

        Returns:
            bool: True if race results are present, False if no race occured.
        '''
        event = self.driver.find_elements(
            By.XPATH,
            '//div[@id="errorContainer"]'
        )
        abandoned = self.driver.current_url != link
        return (bool(event) or bool(abandoned))

    def _create_date_list(self, days: int) -> list():
        '''Get a range of datetimes.

        Creates a range of datetimes of specified length, starting with
        the previous day.

        Args:
            days (int): The number of days to return.

        Returns:
            list (datetime): A list of datetimes in reverse chronological
            order, starting with the previous day.
        '''
        start = datetime.datetime.today() - datetime.timedelta(days=1)
        return [start - datetime.timedelta(days=x) for x in range(days)]

    def _save_data(self, data: dict) -> None:
        ''' Save Dictionary to JSON

        Create a sub-directory in /raw_data/ named with the id, and save
        dict to JSON file.

        Args:
            data (dict): Dictionary with "id" key, to be saved to JSON.
        '''
        id = data['id']
        folder = os.path.join((self.raw_data_path), id)
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(os.path.join(folder, f'{id}.json'), 'w') as f:
            json.dump(data, f, indent=4)

    def _save_image(self, link: str, id: str) -> bool:
        '''Save photo finish.

        Save image of race finish in /raw_data sub-directory, with
        corrasponding JSON. Will atempt to find image 3 times.

        Args:
            link (str): URL link to the image.
            id (str): id field of corrasponding JSON. Used as image name.
        Returns:
            bool: True if image has been saved with urllib.
        '''
        folder = os.path.join((self.raw_data_path), id)
        if not os.path.exists(folder):
            os.makedirs(folder)
        for tries in range(3):
            try:
                self.driver.get(link)
                time.sleep(2)
                img = self.driver.find_element(
                    By.XPATH, '/html/body/img').get_attribute('src')
                urllib.request.urlretrieve(
                    img, os.path.join(folder, f'{id}.jpg')
                    )
                return True
            except urllib.error.URLError:
                print(f'URL error occured: {tries} attempts')
        return False
