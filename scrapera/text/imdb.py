import os
import time
import sqlite3
import urllib.request
import urllib.parse

from bs4 import BeautifulSoup as _BeautifulSoup
from tqdm import tqdm


class IMDBReviewsScraper:
    '''
    Scraper for IMDB Movie Reviews. Data is written to a SQLite file
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

    def _get_id(self, query):

        url = 'https://www.imdb.com/find?' + urllib.parse.urlencode({'q': query, 'ref_': 'nv_sr_sm'})
        req = urllib.request.Request(url, headers=self.headers)
        response = urllib.request.urlopen(req)

        bs4_page = _BeautifulSoup(response.read(), 'lxml')
        anchor_tag = bs4_page.find('td', {'class': 'result_text'}).find('a')['href']
        return anchor_tag.split('/')[2]

    def _get_reviews(self, query, conn, cursor, num_scrolls=1, sleep=5, proxies=None):

        if proxies:
            handler = urllib.request.ProxyHandler(proxies)
            opener = urllib.request.build_opener(handler)
            urllib.request.install_opener(opener)

        id_ = self._get_id(query)
        url = f'https://www.imdb.com/title/{id_}/reviews/?ref_=tt_ql_urv'
        req = urllib.request.Request(url, headers=self.headers)
        resp = urllib.request.urlopen(req).read()
        bs4_page = _BeautifulSoup(resp, 'lxml')

        try:
            page_key = bs4_page.find('div', {'class': 'load-more-data'})['data-key']
        except TypeError:
            raise TypeError("ERROR: Excessive requests. Increase sleep time or using proxies for longer scraping")

        for review in bs4_page.findAll('div', {'class': 'review-container'}):
            # Sometimes the rating doesn't render appropriately
            try:
                rating = review.find('span', {'class': 'rating-other-user-rating'}).find('span').text
            except Exception:
                rating = None

            cursor.execute("INSERT INTO REVIEWS VALUES (?,?,?,?,?)",
                           (None, review.find('div', {'class': 'text'}).text, rating,
                            review.find('span', {'class': 'display-name-link'}).text,
                            review.find('a', {'class': 'title'}).text))
        conn.commit()
        print(f"Sleeping for {sleep} seconds to avoid excessive requests")
        time.sleep(sleep)

        for _ in tqdm(range(num_scrolls)):
            pagination_url = f'https://www.imdb.com/title/{id_}/reviews/_ajax?ref_=undefined&paginationKey={page_key}'
            req = urllib.request.Request(pagination_url)
            resp = urllib.request.urlopen(req).read()
            bs4_page = _BeautifulSoup(resp, 'lxml')
            try:
                page_key = bs4_page.find('div', {'class': 'load-more-data'})['data-key']
            except TypeError:
                raise TypeError("ERROR: Excessive requests. Increase sleep time or using proxies for longer scraping")

            for review in bs4_page.findAll('div', {'class': 'review-container'}):
                try:
                    rating = review.find('span', {'class': 'rating-other-user-rating'}).find('span').text
                except Exception:
                    rating = None

                cursor.execute("INSERT INTO REVIEWS VALUES (?,?,?,?,?)",
                               (None, review.find('div', {'class': 'text'}).text, rating,
                                review.find('span', {'class': 'display-name-link'}).text,
                                review.find('a', {'class': 'title'}).text))
            conn.commit()
            print(f"Sleeping for {sleep} seconds to avoid excessive requests")
            time.sleep(sleep)

    def scrape(self, query, num_scrolls=1, sleep=5, out_path=None):
        '''
        query: str, Movie or Series name for which reviews are to be scraped
        num_scrolls: int, Number of times page should be scrolled. Each scroll will fetch 25 reviews
        sleep: float, Time to sleep (in seconds) between scrolls. Prevents excessive requests and blocking. Default: 5 seconds
        out_path: str, Path to output directory
        '''
        if out_path:
            assert os.path.isdir(out_path), "Invalid path to output directory"

        assert query, "Invalid Query"
        assert num_scrolls >= 0, "Number of scrolls cannot be negative"

        out_path = os.path.join(out_path, f'IMDB-{query.replace(" ", "-")}-Reviews.db') if out_path else f'IMBD-{query.replace(" ", "-")}-Reviews.db'
        conn = sqlite3.connect(out_path)
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS REVIEWS (ID INTEGER PRIMARY KEY AUTOINCREMENT, REVIEW TEXT, RATING NUMBER, AUTHOR VARCHAR(255), TITLE TEXT)")

        self._get_reviews(query.replace(' ', '+'), conn, cursor, num_scrolls, sleep)
        print(f"Finished scraping. All results are stored in {out_path} file")
