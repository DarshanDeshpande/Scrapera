import time

import numpy as _np
import pandas as _pd

import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm


class StocksScraper:
    def __init__(self, driver_path, chromedriver_proxy=None):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('log-level=3')
        if chromedriver_proxy is not None:
            webdriver.DesiredCapabilities.CHROME['proxy'] = chromedriver_proxy
        self.driver = webdriver.Chrome(driver_path,
                                       options=chrome_options)
        self.proxy = chromedriver_proxy

    def _scrape_all_recent(self, num_comp, freq="1d"):
        all_data, company_names, timestamp = [], [], []

        req = urllib.request.Request('https://www.livemint.com/market/market-stats/bse-most-active-stocks-by-volume')
        req.add_header('User-Agent',
                       'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17')

        if self.proxy:
            handler = urllib.request.ProxyHandler(self.proxy)
            opener = urllib.request.build_opener(handler)
            urllib.request.install_opener(opener)

        content = urllib.request.urlopen(req).read()
        bs4_page = BeautifulSoup(content, 'lxml')

        anchor_tags = bs4_page.find_all('a', attrs={'class': 'anchorhover2'}, href=True)
        links = ['https://www.livemint.com' + a['href'] for a in anchor_tags]

        for link in tqdm(links[:num_comp]):
            try:
                if 'market-stats' in link:
                    self.driver.get(link)
                    time.sleep(2)
                    company_name = self.driver.execute_script(
                        "return document.getElementsByClassName('compName')[0].innerText")
                    self.driver.find_element_by_id(freq).click()
                    data = self.driver.execute_script('return Highcharts.charts[0].series[0].yData')
                    timestamp = self.driver.execute_script('return Highcharts.charts[0].series[0].xData')

                    if len(data) != 83 and len(timestamp) != 83:
                        data = self.driver.execute_script('return Highcharts.charts[1].series[0].yData')
                        timestamp = self.driver.execute_script('return Highcharts.charts[1].series[0].xData')

                    if data is not None:
                        print(f"Scraped {len(data)} stocks for {company_name}")
                        all_data.append(data)
                        company_names.append(company_name)
            except Exception:
                continue

        df = _pd.DataFrame(_np.array(all_data).T, columns=company_names)
        df.insert(0, 'Time', timestamp)
        df.to_csv("StockData.csv", index=False)
        print("Finished scraping!")

    def scrape(self, num_companies, freq="1d"):
        assert freq in ['1d', '1m', '3m',
                        '6m','1y'], "Invalid frequency. Available options are ['1d','1m','3m','6m','1y']"

        self._scrape_all_recent(num_companies, freq)
