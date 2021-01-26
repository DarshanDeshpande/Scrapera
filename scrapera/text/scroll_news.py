import os
import sqlite3
import time

import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from tqdm import tqdm


class ScrollScraper:
    '''
    Scraper of Scroll News Articles
    Dependencies: Chromedriver
    Args:
        driver_path: str, Path to chromedriver executable file
        out_path:  [Optional] str, Path to output directory. If unspecified, current directory will be used
        chromedriver_proxy: dict, A dictionary containing proxy information for the webdriver
    '''
    def __init__(self, driver_path, out_path=None, chromedriver_proxy=None):

        assert os.path.isfile(driver_path), "Invalid Chromedriver path received"

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('log-level=3')
        if chromedriver_proxy is not None:
            webdriver.DesiredCapabilities.CHROME['proxy'] = chromedriver_proxy
        self.driver = webdriver.Chrome(driver_path, options=chrome_options)

        print("Output file: ",
              os.path.join(out_path, 'ScrollScraperArticles.db') if out_path else 'ScrollScraperArticles.db')

        self.conn = sqlite3.connect(
            os.path.join(out_path, 'ScrollScraperArticles.db') if out_path else 'ScrollScraperArticles.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS ARTICLES (ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                            "CONTENT TEXT,"
                            "AUTHOR TEXT,"
                            "LINK TEXT)")

        self.proxy = chromedriver_proxy

    def _get_links(self, num_scrolls):
        self.driver.get('https://www.scroll.in/global/')
        for _ in range(num_scrolls):
            self.driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')
            time.sleep(2)

        links_list = set()
        page = BeautifulSoup(self.driver.page_source, 'lxml')
        li_tags = page.findAll('li', {'class': 'row-story'})
        for li in li_tags:
            a_list = li.findAll('a')
            for a in a_list:
                links_list.add(a['href'])

        return links_list

    def _get_article_content(self, all_links, sleep=3):
        for link in tqdm(all_links):
            req = urllib.request.Request(link)
            req.add_header('User-Agent',
                           'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17')
            if self.proxy:
                handler = urllib.request.ProxyHandler(self.proxy)
                opener = urllib.request.build_opener(handler)
                urllib.request.install_opener(opener)

            resp = urllib.request.urlopen(req).read()
            page = BeautifulSoup(resp, 'lxml')
            author = page.find('a', {'rel': 'author'}).contents[0]
            p_tags = page.find('div', {'id': 'article-contents'}).findAll('p')
            article_contents = []
            for p in p_tags:
                article_contents.append(p.text)
            full_content = '\n'.join(article_contents)
            if full_content != '':
                self.cursor.execute("INSERT INTO ARTICLES VALUES (?,?,?,?)", (None, full_content, author, link))
                self.conn.commit()
            time.sleep(sleep)

    def scrape(self, num_scrolls=1, sleep=3):
        '''
        Scraper function
        num_scrolls: int, Number of times to fetch more entries. Default is 1
        sleep: Amount of time to sleep to avoid excessive requests error or blocking
        '''
        assert num_scrolls >= 0, "Number of scrolls cannot be less than zero"
        assert  sleep >= 0, "Sleep time cannot be negative"
        all_links = self._get_links(num_scrolls)
        self._get_article_content(all_links, sleep)
        self.conn.close()
        self.driver.close()
