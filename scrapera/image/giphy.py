import os
import time
import urllib.request

from PIL import Image
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm


class GiphyScraper:
    '''
    Class for Giphy based GIF scraping
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

    def _get_links(self, query, num_scrolls):
        self.driver.get(f"https://giphy.com/search/{query}")

        for _ in range(num_scrolls):
            self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(2)

        links = []
        bs4_page = BeautifulSoup(self.driver.page_source, 'lxml')
        img_tags = bs4_page.findAll('source')
        for gif in img_tags:
            links.append(gif['srcset'])

        return links

    def _get_gifs(self, query, all_links, sleep=3, out_path=None):
        if self.proxy:
            handler = urllib.request.ProxyHandler(self.proxy)
            opener = urllib.request.build_opener(handler)
            urllib.request.install_opener(opener)

        print("-" * 75)
        print(f"Found {len(all_links)} GIFs. Starting download")

        for index, link in tqdm(enumerate(all_links)):
            path = os.path.join(out_path, query.replace("+", "_") + f'{index}') if out_path else f'{query.replace("+", "_")}_{index}'
            urllib.request.urlretrieve(link, path + '.webp')
            im = Image.open(path + '.webp')
            im.info.pop('background', None)
            im.save(f'{path}.gif', 'gif', save_all=True)
            os.remove(path + '.webp')
            print(f"Sleeping for {sleep} seconds to avoid excessive requests")
            time.sleep(sleep)
        print("Finished Downloading")
        print("-" * 75)

    def scrape(self, query, num_scrolls, sleep=3, out_path=None):
        '''
        query: str, Keywords used for fetching
        num_scrolls: int, Number of times to fetch more entries
        sleep: Amount of time(seconds) to sleep while fetching to avoid excessive retries or blocking.
        out_path:  [Optional] str, Path to output directory. If unspecified, current directory will be used
        '''
        query = str(query).replace(' ', '+')
        if out_path is not None:
            out_path = out_path if os.path.isdir(out_path) else None
        all_links = self._get_links(query, num_scrolls)
        self._get_gifs(query, all_links, sleep, out_path)
        self.driver.close()
