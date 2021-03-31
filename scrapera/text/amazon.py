import asyncio
import os
import random
import re
import warnings

import aiohttp
import aiosqlite
from bs4 import BeautifulSoup


class AmazonReviewScraper:
    '''
    Reviews Scraper for Amazon products
    '''

    def __init__(self):
        self.proxies = None

    async def _get_response(self, session, url, get_headers):
        if self.proxies:
            for _ in range(len(self.proxies) + 1):
                try:
                    proxy = random.choice(self.proxies)
                    async with session.get(url, headers=get_headers, proxy=proxy, timeout=3) as response:
                        try:
                            _ = BeautifulSoup(await response.text(), 'lxml').find('input', {'name': 'qid'})['value']
                        except TypeError:
                            continue
                        return await response.read()
                except (
                        asyncio.TimeoutError, aiohttp.client.ClientProxyConnectionError,
                        aiohttp.client.ClientHttpProxyError,
                        aiohttp.client.ServerDisconnectedError, aiohttp.client.ClientOSError):
                    try:
                        self.proxies.remove(proxy)
                    except ValueError:
                        pass
                    continue
        else:
            async with session.get(url, headers=get_headers) as response:
                assert response.status == 200
                return await response.read()

    async def _post_response(self, session, page, query, qid, post_headers):
        url = f'https://www.amazon.com/s/query?k={query}&page={page}&qid={qid}&ref=sr_pg_1'
        if self.proxies:
            for _ in range(len(self.proxies) + 1):
                try:
                    proxy = random.choice(self.proxies)
                    async with session.post(url, headers=post_headers, proxy=proxy, timeout=2) as response:
                        return await response.read()
                except (
                        asyncio.TimeoutError, aiohttp.client.ClientProxyConnectionError,
                        aiohttp.client.ClientHttpProxyError,
                        aiohttp.client.ServerDisconnectedError, aiohttp.client.ClientOSError):
                    try:
                        self.proxies.remove(proxy)
                    except ValueError:
                        pass
                    continue
        else:
            async with session.post(url, headers=post_headers) as response:
                assert response.status == 200
                return await response.read()

    async def _get_links(self, session, query, page, qid):
        post_headers = {'authority': 'www.amazon.com', 'method': 'POST', 'scheme': 'https', 'accept': 'text/html,*/*',
                        'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9',
                        'cache-control': 'no-cache', 'content-type': 'application/json', 'dnt': '1', 'downlink': '10',
                        'ect': '4g', 'origin': 'https://www.amazon.com', 'pragma': 'no-cache', 'rtt': '50',
                        'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36',
                        'x-amazon-s-mismatch-behavior': 'FALLBACK',
                        'x-amazon-s-swrs-version': '57AA0C4FB9DB7B053343F9AB93B43C3D,D41D8CD98F00B204E9800998ECF8427E',
                        'x-requested-with': 'XMLHttpRequest',
                        'path': f'/s/query?k={query}&page={page}&qid={qid}&ref=sr_pg_1',
                        'referer': f'https://www.amazon.com/s?k={query}',
                        'x-amazon-s-fallback-url': f'https://www.amazon.com/s?k={query}&page={page}&qid={qid}&ref=sr_pg_2'}

        parsed_string = await self._post_response(session, page, query, qid, post_headers)
        links = list({'https://amazon.com' + i['href'] for i in
                         BeautifulSoup(parsed_string.decode().replace('\\', ''), 'lxml').findAll('a', {
                             'class': 'a-link-normal'}) if re.match(r'/.*/dp/.*/', i['href'])})
        return links

    async def _write_to_db(self, author, rating, review, title, cursor, db):
        await cursor.execute("INSERT OR IGNORE INTO REVIEWS (AUTHOR, TITLE, REVIEW, RATING) VALUES (?,?,?,?)",
                             (author, title, review, rating))
        await db.commit()

    async def _get_review_page(self, session, page, name, query, id_, qid, db, cursor):

        authors, titles, ratings, reviews = [], [], [], []

        get_headers = {'authority': 'www.amazon.com', 'method': 'GET', 'scheme': 'https',
                       'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                       'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9',
                       'cache-control': 'no-cache', 'dnt': '1', 'downlink': '10', 'ect': '4g', 'pragma': 'no-cache',
                       'rtt': '100', 'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate',
                       'sec-fetch-site': 'none', 'sec-fetch-user': '?1', 'upgrade-insecure-requests': '1',
                       'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36',
                       'referer': f'https://www.amazon.com/{name}/dp/{id_}/ref=sr_1_156_sspa?dchild=1&keywords={query}&qid={qid}&sr=8-156-spons&th=1&psc=1',
                       'path': f'/{name}/product-reviews/{id_}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews'}

        url = f'https://www.amazon.com/{name}/product-reviews/{id_}/ref=cm_cr_getr_d_paging_btm_next_{page + 1}?ie=UTF8&reviewerType=all_reviews&pageNumber={page + 1}'
        resp = await self._get_response(session, url, get_headers)
        content = BeautifulSoup(resp, 'lxml')

        review_divs = content.findAll('div', {"data-hook": "review"})

        for review_div in review_divs:
            try:
                authors.append(review_div.find('a').find('span').text)
            except AttributeError:
                warnings.warn("Exception while getting author:")
                authors.append(None)
            try:
                ratings.append(review_div.find('i', {'data-hook': 'review-star-rating'}).find('span').text)
            except AttributeError:
                warnings.warn("Exception while getting rating:")
                ratings.append(None)
            try:
                reviews.append(review_div.find('span', {'data-hook': 'review-body'}).find('span').text)
            except AttributeError:
                warnings.warn("Exception while getting review:")
                reviews.append(None)
            try:
                titles.append(review_div.find('a', {'data-hook': 'review-title'}).find('span').text)
            except AttributeError:
                warnings.warn("Exception while getting title:")
                titles.append(None)
        coros = [self._write_to_db(author, rating, review, title, cursor, db) for author, rating, review, title in
                 zip(authors, ratings, reviews, titles)]
        await asyncio.gather(*coros)

    async def _process_link(self, session, link, num_review_pages, query, qid, db, cursor):
        name = link.split('/')[3]
        id_ = link.split('/')[5]
        coros = [self._get_review_page(session, page, name, query, id_, qid, db, cursor) for page in
                 range(num_review_pages)]
        await asyncio.gather(*coros)

    async def _main_exec(self, query, num_pages, num_review_pages, out_path):
        async with aiosqlite.connect(out_path) as db:
            cursor = await db.cursor()
            cursor = await db.cursor()
            await cursor.execute("CREATE TABLE IF NOT EXISTS REVIEWS (ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                                 "AUTHOR VARCHAR(255),"
                                 "TITLE TEXT,"
                                 "REVIEW TEXT UNIQUE,"
                                 "RATING VARCHAR(25))")

            async with aiohttp.ClientSession() as session:
                get_headers = {'authority': 'www.amazon.com', 'method': 'GET', 'scheme': 'https',
                               'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                               'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9',
                               'cache-control': 'no-cache', 'dnt': '1', 'downlink': '10', 'ect': '4g',
                               'pragma': 'no-cache', 'rtt': '100', 'sec-fetch-dest': 'document',
                               'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'none', 'sec-fetch-user': '?1',
                               'upgrade-insecure-requests': '1',
                               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36',
                               'path': f'/s?k={query}&ref=nb_sb_noss_1'}

                url = f'https://www.amazon.com/s?k={query}&ref=nb_sb_noss_1'
                response = await self._get_response(session, url, get_headers)
                assert response is not None, "All proxies exhausted. Retry with working proxies"
                qid = BeautifulSoup(response, 'lxml').find('input', {'name': 'qid'})['value']
                assert qid is not None, "Did not find Q-ID"

                coros = [self._get_links(session, query, page, qid) for page in range(1, num_pages + 2, 1)]
                links = await asyncio.gather(*coros)
                links = set(sum(links, []))

                coros = [self._process_link(session, link, num_review_pages, query, qid, db, cursor) for link in
                         links]
                await asyncio.gather(*coros)

    def scrape(self, query, num_product_pages, num_review_pages, out_path=None, proxies=None):
        '''
        query: str, Query for which reviews are to be scraped.
        num_products: int, Number of product pages to be scraped. Each page has approximately 25 products
        num_review_pages: int, Number of pages of reviews to be scraped for each review. Each page has 10 reviews
        out_path:  str, Path to output directory
        proxies: list, list of HTTP/Upgradable HTTPS proxies. These proxies are automatically rotated
        '''
        assert num_product_pages >= 1 and type(
            num_product_pages) is int, "Number of product pages cannot be zero or negative"
        assert num_review_pages >= 1 and type(
            num_review_pages) is int, "Number of review pages cannot be zero or negative"
        if out_path:
            assert os.path.isdir(out_path), "Invalid output directory"
        if proxies:
            assert type(proxies) is list or type(proxies) is tuple, "'proxies' must be a list"
            self.proxies = proxies

        out_path = os.path.join(out_path, 'AmazonProductReviews.db') if out_path else 'AmazonProductReviews.db'
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._main_exec(query, num_product_pages, num_review_pages, out_path))
        loop.close()
