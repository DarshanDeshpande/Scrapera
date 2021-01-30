import os
import re
import sqlite3
import time
import warnings

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

warnings.filterwarnings('ignore')


class VOAScraper:
    '''
    Scraper for Voice of America News Articles
    '''
    def __init__(self):
        self.get_headers = {'authority': 'www.voanews.com',
                            'method': 'GET',
                            'path': '/usa',
                            'scheme': 'https',
                            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                            'accept-encoding': 'gzip, deflate, br',
                            'accept-language': 'en-US,en;q=0.9',
                            'cache-control': 'no-cache',
                            'dnt': '1',
                            'pragma': 'no-cache',
                            'referer': 'https://www.voanews.com/',
                            'sec-fetch-dest': 'document',
                            'sec-fetch-mode': 'navigate',
                            'sec-fetch-site': 'same-origin',
                            'sec-fetch-user': '?1',
                            'upgrade-insecure-requests': '1',
                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'}

        self.post_headers = {'authority': 'www.voanews.com',
                             'method': 'POST',
                             'path': '/views/ajax?_wrapper_format=drupal_ajax',
                             'scheme': 'https',
                             'accept': 'application/json, text/javascript, */*; q=0.01',
                             'accept-encoding': 'deflate',
                             'accept-language': 'en-US,en;q=0.9',
                             'cache-control': 'no-cache',
                             'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                             'dnt': '1',
                             'origin': 'https://www.voanews.com',
                             'pragma': 'no-cache',
                             'referer': 'https://www.voanews.com/usa',
                             'sec-fetch-dest': 'empty',
                             'sec-fetch-mode': 'cors',
                             'sec-fetch-site': 'same-origin',
                             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36',
                             'x-requested-with': 'XMLHttpRequest'}

        self.session = requests.Session()

    def _get_links(self, num_pages=1, sleep=1):
        all_links = []
        resp = self.session.get('https://www.voanews.com/usa', headers=self.get_headers).content.decode()
        view_dom_id = re.findall(r'"view_dom_id":"[^"]*"', resp)[0].split(':')[-1].replace('"', '')
        bs4_page = BeautifulSoup(resp, 'lxml')
        anchor_tags = bs4_page.findAll('a', {'class': 'teaser__title-link'})
        for a in anchor_tags:
            all_links.append(a['href'])

        for page in range(num_pages):
            resp = self.session.post('https://www.voanews.com/views/ajax?_wrapper_format=drupal_ajax',
                                     headers=self.post_headers, data={'view_name': 'taxonomy_term',
                                                                      'view_display_id': 'related_content',
                                                                      'view_args': '32681',
                                                                      'view_path': '/taxonomy/term/32681',
                                                                      'view_base_path': 'taxonomy/term/%/feed',
                                                                      'view_dom_id': view_dom_id,
                                                                      'pager_element': '0',
                                                                      'page': page + 1,
                                                                      '_drupal_ajax': '1',
                                                                      'ajax_page_state[theme]': 'voa',
                                                                      'ajax_page_state[libraries]': 'blazy/load,core/html5shiv,core/picturefill,paragraphs/drupal.paragraphs.unpublished,poll/drupal.poll-links,system/base,views/views.module,views_infinite_scroll/views-infinite-scroll,voa/bower,voa/global,voa_breaking_news/breaking-news,voa_media_schedule/menu_block,voa_tracking_code/voa_tracking_code'})

            # Returned HTTP Response has unknown encoding with unnecessary '\\'.
            # Python's deprecation warning for re.sub() is suppressed for now
            resp = re.sub(r'\\', '', resp.content.decode('unicode_escape'))
            bs4_page = BeautifulSoup(resp, 'lxml')
            anchor_tags = bs4_page.findAll('a', {'class': 'teaser__title-link'})
            for a in anchor_tags:
                all_links.append(a['href'])

            if sleep != 0:
                print(f"Sleeping {sleep} seconds to avoid excessive requests")
                time.sleep(sleep)

        return all_links

    def _get_content(self, conn, cursor, num_pages, sleep):
        links = self._get_links(num_pages, sleep)
        for link in tqdm(links):
            full_text = ''
            self.get_headers['path'] = link
            resp = self.session.get("https://www.voanews.com" + link, headers=self.get_headers)
            bs4_page = BeautifulSoup(resp.content, 'lxml')
            try:
                title = bs4_page.find('h1', {'class': 'page-header__title'}).find('span').get_text(strip=True)
                author = bs4_page.find('div', {'class': 'page-header__meta-item'}).findAll('span')[-1].get_text(
                    strip=True)
                body = bs4_page.find('div', {'class': 'article__body'}).find('div').findAll('p')
                for p in body:
                    full_text += p.get_text(strip=True)
            except Exception:
                continue
            cursor.execute("INSERT INTO ARTICLES (TITLE, CONTENT, AUTHOR) VALUES (?,?,?)", (title, full_text, author))
            conn.commit()
            if sleep != 0:
                print(f"Sleeping {sleep} seconds to avoid excessive requests")
                time.sleep(sleep)
        print("Finished Scraping")

    def scrape(self, num_pages=1, out_path=None, sleep=3, proxies=None):
        '''
        num_pages: int, Number of pages to scrape. Each page has approximately 15 articles
        out_path: str, Path to output directory
        sleep: float, Amount of time to sleep between requests to avoid HTTP 429 (Excessive Requests)
        proxies: dict, HTTP/HTTPS proxies
        '''
        assert num_pages >= 1, "Number of pages to be scraped cannot be zero or negative"
        assert sleep >= 0, "Amount of time to sleep cannot be negative"
        if out_path:
            assert os.path.isdir(out_path), "Invalid output directory"

        if proxies:
            assert type(proxies) is dict, "Invalid proxies received. 'proxies' must be of type dict"
            self.session.proxies = proxies

        conn = sqlite3.connect(
            os.path.join(out_path, 'VOAArticles.db') if out_path else 'VOAArticles.db')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS ARTICLES (ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                       "TITLE TEXT,"
                       "CONTENT TEXT,"
                       "AUTHOR TEXT)")

        self._get_content(conn, cursor, num_pages, sleep)
