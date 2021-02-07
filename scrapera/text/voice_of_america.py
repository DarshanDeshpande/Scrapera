import asyncio
import os
import random
import re
import warnings

import aiohttp
import aiosqlite
from bs4 import BeautifulSoup

warnings.filterwarnings('ignore')


class VOAScraper:
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

        self.proxies = None

    async def _get_response(self, session, url):
        if self.proxies:
            for _ in range(len(self.proxies)):
                try:
                    proxy = random.choice(self.proxies)
                    async with session.get(url, headers=self.get_headers, proxy=proxy, timeout=3) as response:
                        assert response.status == 200
                        return await response.read()
                except (asyncio.TimeoutError, aiohttp.client.ClientProxyConnectionError,
                        aiohttp.client.ClientHttpProxyError, aiohttp.client.ServerDisconnectedError,
                        aiohttp.client.ClientOSError):
                    try:
                        self.proxies.remove(proxy)
                        if not self.proxies:
                            raise AssertionError("Exhausted all proxies. Ensure that your proxies are valid")
                    except ValueError:
                        pass
                    continue
        else:
            async with session.get(url, headers=self.get_headers) as response:
                assert response.status == 200, "Could not connect. Check your internet connection"
                return await response.read()

    async def _post_response(self, session, url, data):
        if self.proxies:
            for _ in range(len(self.proxies)):
                try:
                    proxy = random.choice(self.proxies)
                    async with session.post(url, headers=self.post_headers, data=data) as response:
                        assert response.status == 200
                        text = await response.text()
                        return re.sub(r'\\', '', text.encode().decode('unicode_escape'))
                except (asyncio.TimeoutError, aiohttp.client.ClientProxyConnectionError,
                        aiohttp.client.ClientHttpProxyError, aiohttp.client.ServerDisconnectedError,
                        aiohttp.client.ClientOSError):
                    try:
                        self.proxies.remove(proxy)
                        if not self.proxies:
                            raise AssertionError("Exhausted all proxies. Ensure that your proxies are valid")
                    except ValueError:
                        pass
                    continue
        else:
            async with session.post(url, headers=self.post_headers, data=data) as response:
                assert response.status == 200
                text = await response.text()
                return re.sub(r'\\', '', text.encode().decode('unicode_escape'))

    async def _get_anchors(self, resp):
        all_links = []
        bs4_page = BeautifulSoup(resp, 'lxml')
        anchor_tags = bs4_page.findAll('a', {'class': 'teaser__title-link'})
        for a in anchor_tags:
            all_links.append(a['href'])

        return all_links

    async def _write_to_db(self, session, link, db, cursor):
        full_text = ''
        self.get_headers['path'] = link
        try:
            resp = await self._get_response(session, "https://www.voanews.com" + link)
        except Exception:
            raise

        bs4_page = BeautifulSoup(resp, 'lxml')
        try:
            title = bs4_page.find('h1', {'class': 'page-header__title'}).find('span').get_text(strip=True)
            author = bs4_page.find('div', {'class': 'page-header__meta-item'}).findAll('span')[-1].get_text(
                strip=True)
            body = bs4_page.find('div', {'class': 'article__body'}).find('div').findAll('p')
            for p in body:
                full_text += p.get_text(strip=True)
        except AttributeError:
            return
        await cursor.execute("INSERT INTO ARTICLES (TITLE, CONTENT, AUTHOR) VALUES (?,?,?)", (title, full_text, author))
        await db.commit()

    async def _main_exec(self, num_pages, out_path):
        async with aiosqlite.connect(out_path) as db:
            cursor = await db.cursor()
            await cursor.execute("CREATE TABLE IF NOT EXISTS ARTICLES (ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                                 "TITLE TEXT,"
                                 "CONTENT TEXT,"
                                 "AUTHOR TEXT)")

            all_links = []
            async with aiohttp.ClientSession() as session:
                try:
                    resp = await self._get_response(session, 'https://www.voanews.com/usa')
                except Exception:
                    raise
                view_dom_id = re.findall(r'"view_dom_id":"[^"]*"', resp.decode())[0].split(':')[-1].replace('"', '')
                bs4_page = BeautifulSoup(resp, 'lxml')
                anchor_tags = bs4_page.findAll('a', {'class': 'teaser__title-link'})

                for a in anchor_tags:
                    all_links.append(a['href'])

                try:
                    coros = [
                        self._post_response(session, 'https://www.voanews.com/views/ajax?_wrapper_format=drupal_ajax',
                                            data={'view_name': 'taxonomy_term',
                                                  'view_display_id': 'related_content',
                                                  'view_args': '32681',
                                                  'view_path': '/taxonomy/term/32681',
                                                  'view_base_path': 'taxonomy/term/%/feed',
                                                  'view_dom_id': view_dom_id,
                                                  'pager_element': '0',
                                                  'page': page + 1,
                                                  '_drupal_ajax': '1',
                                                  'ajax_page_state[theme]': 'voa',
                                                  'ajax_page_state[libraries]': 'blazy/load,core/html5shiv,core/picturefill,paragraphs/drupal.paragraphs.unpublished,'
                                                                                'poll/drupal.poll-links,system/base,views/views.module,views_infinite_scroll/views-infinite-scroll,'
                                                                                'voa/bower,voa/global,voa_breaking_news/breaking-news,voa_media_schedule/menu_block,'
                                                                                'voa_tracking_code/voa_tracking_code'})
                        for page in
                        range(num_pages)]
                except Exception:
                    raise
                responses = await asyncio.gather(*coros)

                coros = [self._get_anchors(resp) for resp in responses]
                links = await asyncio.gather(*coros)
                links = sum(links, [])

                coros = [self._write_to_db(session, link, db, cursor) for link in links]
                await asyncio.gather(*coros)

    def scrape(self, num_pages, out_path=None, proxies=None):
        '''
        num_pages: int, Number of pages to be scraped
        out_path: str, Path to output directory
        proxies: list, list of HTTP/Upgradable HTTPS proxies. These proxies are automatically rotated
        '''
        if out_path:
            assert os.path.isdir(out_path), "Invalid output directory"
        if proxies:
            assert proxies is not None, "Invalid proxies received"
            self.proxies = proxies
        assert num_pages >= 1, "Number of pages cannot be zero or negative"

        out_path = os.path.join(out_path, 'VOAArticles.db') if out_path else 'VOAArticles.db'
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._main_exec(num_pages, out_path))
        loop.close()
