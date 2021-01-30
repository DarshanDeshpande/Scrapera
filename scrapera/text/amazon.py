import requests
import urllib.parse as urlparse
from urllib.parse import parse_qs
import re
import html
import time
from bs4 import BeautifulSoup
import sqlite3
import os
from tqdm import tqdm


class AmazonReviewScraper:
    '''
    Reviews Scraper for Amazon products
    '''
    def __init__(self):
        self.post_headers = {'authority': 'www.amazon.com',
                             'method': 'POST',
                             'scheme': 'https',
                             'accept': 'text/html,*/*',
                             'accept-encoding': 'gzip, deflate, br',
                             'accept-language': 'en-US,en;q=0.9',
                             'cache-control': 'no-cache',
                             'content-type': 'application/json',
                             'dnt': '1',
                             'downlink': '10',
                             'ect': '4g',
                             'origin': 'https://www.amazon.com',
                             'pragma': 'no-cache',
                             'rtt': '50',
                             'sec-fetch-dest': 'empty',
                             'sec-fetch-mode': 'cors',
                             'sec-fetch-site': 'same-origin',
                             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36',
                             'x-amazon-s-mismatch-behavior': 'FALLBACK',
                             'x-amazon-s-swrs-version': '57AA0C4FB9DB7B053343F9AB93B43C3D,D41D8CD98F00B204E9800998ECF8427E',
                             'x-requested-with': 'XMLHttpRequest'}

        self.get_headers = {'authority': 'www.amazon.com',
                            'method': 'GET',
                            'scheme': 'https',
                            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                            'accept-encoding': 'gzip, deflate, br',
                            'accept-language': 'en-US,en;q=0.9',
                            'cache-control': 'no-cache',
                            'dnt': '1',
                            'downlink': '10',
                            'ect': '4g',
                            'pragma': 'no-cache',
                            'rtt': '100',
                            'sec-fetch-dest': 'document',
                            'sec-fetch-mode': 'navigate',
                            'sec-fetch-site': 'none',
                            'sec-fetch-user': '?1',
                            'upgrade-insecure-requests': '1',
                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'}

        self.session = requests.Session()

    def _get_links(self, query, num_pages=1):

        all_links = []
        self.get_headers['path'] = f'/s?k={query}&ref=nb_sb_noss_1'

        resp = self.session.get(f'https://www.amazon.com/s?k={query}&ref=nb_sb_noss_1', headers=self.get_headers)
        qid = BeautifulSoup(resp.content, 'lxml').find('input', {'name': 'qid'})['value']

        for page in range(2, num_pages + 2, 1):
            self.post_headers['path'] = f'/s/query?k={query}&page={page}&qid={qid}&ref=sr_pg_1'
            self.post_headers['referer'] = f'https://www.amazon.com/s?k={query}'
            self.post_headers[
                'x-amazon-s-fallback-url'] = f'https://www.amazon.com/s?k={query}&page={page}&qid={qid}&ref=sr_pg_2'

            resp = self.session.post(f'https://www.amazon.com/s/query?k=t-shirts&page={page}&qid={qid}&ref=sr_pg_1',
                                     headers=self.post_headers)
            parsed_string = html.unescape(resp.content.decode())
            links = re.findall('"(/gp/slredirect/picassoRedirect.html/.*?)"', parsed_string)
            all_links.extend(links)

            time.sleep(1)

        print(f"Found {len(all_links)} links")
        return list(set(all_links)), qid

    def _get_data(self, query, conn, cursor, num_products=1, num_review_pages=5, sleep=1):

        links, qid = self._get_links(query, num_products)
        for link in tqdm(links):
            parsed = urlparse.urlparse(link)
            name = parse_qs(parsed.query)['url'][0].split('/')[1]
            id_ = re.findall(r'.*\/dp\/(.*)/', parse_qs(parsed.query)['url'][0].encode('utf-8').decode())[0].split('/')[
                -1]

            for page in range(num_review_pages):
                self.get_headers[
                    'referer'] = f'https://www.amazon.com/{name}/dp/{id_}/ref=sr_1_156_sspa?dchild=1&keywords=t-shirts&qid={qid}&sr=8-156-spons&th=1&psc=1'
                self.get_headers[
                    'path'] = f'/{name}/product-reviews/{id_}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'

                url = f'https://www.amazon.com/{name}/product-reviews/{id_}/ref=cm_cr_getr_d_paging_btm_next_{page + 1}?ie=UTF8&reviewerType=all_reviews&pageNumber={page + 1}'
                resp = self.session.get(url, headers=self.get_headers)
                content = BeautifulSoup(resp.content, 'lxml')
                review_divs = content.findAll('div', {"data-hook": "review"})
                for review_div in review_divs:
                    try:
                        author = review_div.find('a').find('span').text
                    except Exception:
                        author = None
                    try:
                        rating = review_div.find('i', {'data-hook': 'review-star-rating'}).find('span').text
                    except Exception:
                        rating = None
                    try:
                        review = review_div.find('span', {'data-hook': 'review-body'}).find('span').text
                    except Exception:
                        review = None
                    try:
                        title = review_div.find('a', {'data-hook': 'review-title'}).find('span').text
                    except Exception:
                        title = None

                    cursor.execute("INSERT INTO REVIEWS (AUTHOR, TITLE, REVIEW, RATING) VALUES (?,?,?,?)",
                                   (author, title, review, rating))
                conn.commit()

            if sleep != 0:
                print(f"Sleeping for {sleep} seconds")
                time.sleep(sleep)

    def scrape(self, query, num_product_pages=1, num_review_pages=5, out_path=None, proxies=None, sleep=1):
        '''
        query: str, Product name that is to be scraped
        num_product_pages: int, Number of pages to scrape. Each page has approximately 25 products
        num_review_pages: int, Number of review pages to be scraped. Each page has 10 reviews
        out_path: str, Path to output directory
        proxies: dict, HTTP/HTTPS proxies
        sleep: float, Amount of time to sleep between requests to avoid HTTP Error 429
        '''
        assert query != '' and type(query) is str, "Invalid product name"
        assert num_product_pages >= 1, "Number of products to be scraped cannot be zero or negative"
        assert num_review_pages >= 1, "Number of comment pages to be scraped cannot be zero or negative"
        if out_path:
            assert os.path.isdir(out_path), "Invalid path to output directory"
        assert sleep >= 0, "Sleep time cannot be negative"

        if proxies:
            assert type(proxies) is dict, "Invalid proxies received. Ensure that the input is of type 'dict' "
            self.session.proxies = proxies

        conn = sqlite3.connect(
            os.path.join(out_path, 'AmazonProductReviews.db') if out_path else 'AmazonProductReviews.db')
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS REVIEWS (ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                       "AUTHOR VARCHAR(255),"
                       "TITLE TEXT,"
                       "REVIEW TEXT,"
                       "RATING NUMBER)")

        print("Database created. Starting scraping procedure")

        self._get_data(query.replace(' ', '+'), conn, cursor, num_product_pages, num_review_pages, sleep)
        conn.close()
