import gzip
import json
import os
import re
import sqlite3
import time
import urllib.request

from bs4 import BeautifulSoup
from tqdm import tqdm


class ScrollScraper:
    '''
    Scraper for Scroll News Articles
    '''

    def __init__(self):
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
                      "application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7",
            "cache-control": "max-age=0",
            "dnt": "1",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/81.0.4044.122 Safari/537.36"}

    def _get_links(self, num_articles, conn, cursor, sleep=1):
        page, counter, flag = 2, 1, False
        url = 'https://scroll.in/global/'
        req = urllib.request.Request(url, headers=self.headers)
        resp = gzip.decompress(urllib.request.urlopen(req).read()).decode()
        offset = re.findall(r'"offset": [0-9]+,', resp)[0][:-1].split(':')[-1].strip()

        while True:
            page_url = f'https://scroll.in/feed/series/15/page/{page}?offset={offset}'
            json_contents = json.loads(urllib.request.urlopen(page_url).read().decode('utf-8'))
            offset = json_contents['offset']

            for article in tqdm(json_contents['articles'][0]['blocks'][0]['articles']):
                if counter <= num_articles:
                    author_name = article['authors'][0]['name']
                    title = article['title']
                    link = article['permalink']
                    req = urllib.request.Request(link, headers=self.headers)
                    resp = gzip.decompress(urllib.request.urlopen(req).read())

                    page_ = BeautifulSoup(resp, 'lxml')
                    p_tags = page_.find('div', {'id': 'article-contents'}).findAll('p')
                    article_contents = []
                    for p in p_tags:
                        article_contents.append(p.text)
                    full_content = '\n'.join(article_contents)
                    cursor.execute("INSERT INTO ARTICLES VALUES (?,?,?,?,?)",
                                (None, title, full_content, author_name, link))
                    conn.commit()

                    if sleep != 0:
                        print(f"Sleeping for {sleep} seconds to avoid excessive requests")
                        time.sleep(sleep)

                    counter += 1
                else:
                    flag = True
                    break

            if flag:
                break

            if sleep != 0:
                print(f"Sleeping for {sleep} seconds to avoid excessive requests")
                time.sleep(sleep)

    def scrape(self, num_articles=1, out_path=None, sleep=1, proxy=None):
        '''
        Scraper function
        num_articles: int, Number of times to fetch more entries. Default is 1
        out_path: str, Path to output directory
        sleep: Amount of time to sleep to avoid excessive requests error or blocking
        proxy: dict, Dictionary containing http/https proxies
        '''
        assert num_articles >= 1, "Number of articles cannot be less than one"
        assert sleep >= 0, "Sleep time cannot be negative"
        if proxy:
            assert type(proxy) is dict, "Invalid proxy details received"
            handler = urllib.request.ProxyHandler(proxy)
            opener = urllib.request.build_opener(handler)
            urllib.request.install_opener(opener)

        print("Output file: ",
              os.path.join(out_path, 'ScrollScraperArticles.db') if out_path else 'ScrollScraperArticles.db')

        conn = sqlite3.connect(
            os.path.join(out_path, 'ScrollScraperArticles.db') if out_path else 'ScrollScraperArticles.db')
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS ARTICLES (ID INTEGER PRIMARY KEY AUTOINCREMENT, TITLE TEXT, "
            "CONTENT TEXT, AUTHOR TEXT, LINK TEXT)")

        self._get_links(num_articles, conn, cursor)
        conn.close()
