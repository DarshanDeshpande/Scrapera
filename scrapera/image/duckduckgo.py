import os
import time

import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm


class DuckDuckGoScraper:
    '''
    Class for DuckDuckGo Image Scraper.
    Dependencies: Chromedriver
    Args:
        driver_path: str, Path to chromedriver executable file
        chromedriver_proxy: dict, A dictionary containing proxy information for the webdriver
    '''
    def __init__(self, driver_path, chromedriver_proxy=None):
        assert os.path.isfile(driver_path), "Incorrect Chromedriver path received"

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('log-level=3')
        if chromedriver_proxy is not None:
            webdriver.DesiredCapabilities.CHROME['proxy'] = chromedriver_proxy
        self.driver = webdriver.Chrome(driver_path, options=chrome_options)

        self.proxy = chromedriver_proxy

    def _scrape_images(self, query, num_scrolls, out_path):

        # Loading the DuckDuckGo image results page
        self.driver.get(f"https://duckduckgo.com/?q={query}&iax=images&ia=images")

        # Scroll num_scroll times
        for _ in range(num_scrolls):
            self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(2)

        # Parse the html to a BS4 object
        page = BeautifulSoup(self.driver.page_source, 'lxml')
        image_tags = page.findAll('img', {'class': 'tile--img__img'})
        image_links = ["https:" + i['data-src'] for i in image_tags]  # Adding https to avoid conflicts during downloading
        print(f"Found {len(image_links)} links")
        print("Beginning download")

        if self.proxy:
            handler = urllib.request.ProxyHandler(self.proxy)
            opener = urllib.request.build_opener(handler)
            urllib.request.install_opener(opener)

        for i, image_link in tqdm(enumerate(image_links)):
            # Deciding the output path based on given directory
            image_save_path = out_path + f"/{query + '_' + str(i)}.jpeg" if out_path else f"/{query + '_' + str(i)}.jpeg"
            urllib.request.urlretrieve(image_link, image_save_path)

    def scrape(self, query, num_scrolls, out_path):
        '''
        query: str, Keywords used for fetching results
        num_scrolls: int, Number of times to fetch more entries
        out_path:  [Optional] str, Path to output directory. If unspecified, current directory will be used
        '''
        query = str(query).replace(' ', '+')
        out_path = out_path if os.path.isdir(out_path) else None
        self._scrape_images(query,num_scrolls,out_path)
