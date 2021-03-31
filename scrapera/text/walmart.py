import asyncio
import json
import logging
import os
import random
import time

import aiohttp
import aiosqlite


class WalmartReviewsScraper:
    """
    Scraper for Walmart Product Reviews
    """
    def __init__(self):
        self.proxies = None
        self.agents = None

    def _agents(self):
        agents = open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'USER-AGENTS.txt')).readlines()
        self.agents = [i.strip() for i in agents if 'download' not in i.lower() and i != '']
        print(f"Found {len(self.agents)} user agents")

    async def _get_response(self, session, url, get_headers):
        if self.proxies:
            for _ in range(len(self.proxies) + 1):
                proxy = random.choice(self.proxies)
                try:
                    async with session.get(url, headers=get_headers, proxy=proxy, timeout=3) as response:
                        try:
                            # This only checks for a valid proxy. This value is not used
                            resp = await response.json()
                            _ = resp['payload']['reviews']
                        except (TypeError, KeyError):
                            continue
                        return await response.json()
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
                return await response.json()

    async def _post_response(self, session, url, data, post_headers):
        if self.proxies:
            for _ in range(len(self.proxies) + 1):
                proxy = random.choice(self.proxies)
                try:
                    async with session.post(url, data=data,
                                            headers=post_headers) as response:
                        try:
                            # This only checks for a valid proxy. This value is not used
                            resp = await response.json()
                            _ = resp['payload']['reviews']
                        except (TypeError, KeyError):
                            continue
                        return await response.json()
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
            async with session.post('https://www.walmart.com/terra-firma/fetch?rgs=REVIEWS_MAP', data=data,
                                    headers=post_headers) as response:
                assert response.status == 200
                return await response.json()

    async def _get_ids(self, session, page, query, sleep):
        while True:
            get_headers = {'authority': 'www.walmart.com',
                           'method': 'GET',
                           'path': f'/search/api/preso?prg=desktop&page={page}&ps=48&query={query}',
                           'scheme': 'https',
                           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/'
                                     'webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                           'accept-encoding': 'gzip, deflate, br',
                           'accept-language': 'en-GB,en;q=0.9',
                           'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
                           'sec-ch-ua-mobile': '?0',
                           'sec-fetch-dest': 'document',
                           'sec-fetch-mode': 'navigate',
                           'sec-fetch-site': 'none',
                           'sec-fetch-user': '?1',
                           'upgrade-insecure-requests': '1',
                           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ('
                                         'KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'}

            url = f'https://www.walmart.com/search/api/preso?prg=desktop&page={page}&ps=48&query={query}'
            try:
                response = await self._get_response(session, url, get_headers)

                if sleep > 0:
                    print("Sleeping between GET requests")
                    time.sleep(sleep)

                item_ids, product_ids = [], []
                for item in response['items']:
                    item_ids.append(item['productId'])
                    product_ids.append(item['usItemId'])
                return item_ids, product_ids

            except (AssertionError, asyncio.TimeoutError):
                try:
                    self.agents.remove(get_headers['user-agent'])
                    logging.warning(f"Failed to send GET request. {len(self.agents)} user-agents left.")
                    continue
                except ValueError:
                    logging.warning(f"Failed to send GET request. {len(self.agents)} user-agents left")
                    continue
            except aiohttp.client.ContentTypeError:
                logging.warning("Redirect received")
                if self.proxies:
                    logging.warning("Trying another proxy")
                    continue
                else:
                    logging.exception("Use a proxy to continue scraping")
                    exit(1)

    @staticmethod
    async def _write_to_db(author, rating, review, product_id, query, cursor, db):
        await cursor.execute("INSERT OR REPLACE INTO REVIEWS (AUTHOR, REVIEW, RATING, PRODUCTID, QUERY) "
                             "VALUES (?,?,?,?,?)",
                             (author, review, rating, product_id, query.capitalize()))
        await db.commit()

    async def get_page_contents(self, session, page, i_id, p_id, query, cursor, db, sleep=5):
        while True:
            payload = json.dumps({'itemId': i_id,
                                  'paginationContext': {'page': page, 'sort': "relevancy",
                                                        'filters': [], 'limit': 20}})
            user_agent = random.choice(self.agents)

            headers = {
                'authority': 'www.walmart.com',
                'method': 'POST',
                'path': '/terra-firma/fetch?rgs=REVIEWS_MAP',
                'scheme': 'https',
                'accept': 'application/json',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-US,en;q=0.9',
                'cache-control': 'no-cache',
                'content-type': 'application/json',
                'dnt': '1',
                'origin': 'https://www.walmart.com',
                'pragma': 'no-cache',
                'referer': f'https://www.walmart.com/reviews/product/{p_id}?page={page}',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': user_agent
            }

            try:
                reviews = await self._post_response(session,
                                                    'https://www.walmart.com/terra-firma/fetch?rgs=REVIEWS_MAP',
                                                    data=payload, post_headers=headers)
                reviews = reviews['payload']['reviews']
            except (AssertionError, KeyError, aiohttp.client.ContentTypeError, asyncio.TimeoutError):
                try:
                    self.agents.remove(headers['user-agent'])
                    logging.warning(f"Failed to send POST request. {len(self.agents)} user-agents left")
                    continue
                except ValueError:
                    logging.warning(f"{len(self.agents)} user-agents left")
                    continue

            if sleep > 0:
                print("Sleeping between POST requests")
                time.sleep(sleep)

            reviews = reviews[list(reviews.keys())[0]]

            reviews_list, authors_list, ratings_list = [], [], []
            try:
                for rev in reviews['customerReviews']:
                    try:
                        reviews_list.append(rev['reviewText'].strip())
                    except KeyError:
                        reviews_list.append(None)
                    try:
                        authors_list.append(rev['userNickname'].strip())
                    except KeyError:
                        authors_list.append(None)
                    try:
                        ratings_list.append(rev['rating'])
                    except KeyError:
                        ratings_list.append(None)
            except TypeError:
                logging.warning("Invalid JSON response received. Moving to the next page")
                return

            coros = [self._write_to_db(author, rating, review, product_id, query, cursor, db)
                     for author, rating, review, product_id in
                     zip(authors_list, ratings_list, reviews_list, [p_id for _ in range(len(authors_list))])]
            await asyncio.gather(*coros)
            return

    async def _get_content(self, session, num_pages, i_id, p_id, query, cursor, db, sleep=5):
        coros = [self.get_page_contents(session, page + 1, i_id, p_id, query, cursor, db, sleep)
                 for page in range(num_pages)]
        await asyncio.gather(*coros)

    async def _main_exec(self, query, num_product_pages, out_path, num_review_pages, sleep=5):
        async with aiosqlite.connect(out_path) as db:
            cursor = await db.cursor()
            await cursor.execute(
                "CREATE TABLE IF NOT EXISTS REVIEWS (ID INTEGER PRIMARY KEY AUTOINCREMENT, REVIEW TEXT, "
                "AUTHOR VARCHAR(100), RATING NUMBER, PRODUCTID VARCHAR(255), QUERY VARCHAR(100))")
            async with aiohttp.ClientSession(trust_env=True) as session:
                coros = [self._get_ids(session, page + 1, query, sleep) for page in range(num_product_pages)]
                ids = await asyncio.gather(*coros)
                item_ids, product_ids = ids[0][0], ids[0][1]

                coros = [self._get_content(session, num_review_pages, i_id, p_id, query, cursor, db, sleep)
                         for index, (i_id, p_id) in
                         enumerate(zip(item_ids, product_ids))]
                await asyncio.gather(*coros)

    def scrape(self, query, num_product_pages, num_review_pages, sleep=5, rotate_agents=True, out_path=None,
               proxies=None):
        """
        query: str, Query for which reviews are to be scraped.
        num_products: int, Number of product pages to be scraped. Each page has approximately 25 products
        num_review_pages: int, Number of review pages to be scraped for each product. Each page has approximately 20 reviews
        sleep: float, Seconds to sleep between requests
        rotate_agents: bool, Download and rotate random user-agents
        out_path:  str, Path to output directory
        proxies: list, list of HTTP/Upgradable HTTPS proxies. These proxies are automatically rotated
        """
        assert type(query) is str and len(query) > 0, "Invalid query received"
        assert num_product_pages >= 1 and type(
            num_product_pages) is int, "Number of product pages cannot be zero or negative"
        assert (num_review_pages >= 0) and type(
            num_review_pages) is int, "Number of review pages cannot be zero or negative"
        assert sleep >= 0, "Sleep time cannot be negative"
        if out_path:
            assert os.path.isdir(out_path), "Invalid output directory"
        if proxies:
            assert type(proxies) is list or type(proxies) is tuple, "'proxies' must be a list"
            self.proxies = proxies
        if rotate_agents:
            assert type(rotate_agents) is bool, "'rotate_agents' should be a boolean value"
            self._agents()
        else:
            self.agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36']

        out_path = os.path.join(out_path, 'WalmartReviews.db') if out_path else 'WalmartReviews.db'
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._main_exec(query, num_product_pages, out_path, num_review_pages, sleep))
        loop.close()
