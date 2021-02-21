import asyncio
import json
import os
import uuid
import random
import aiofiles
import aiohttp
import warnings
from bs4 import BeautifulSoup


class TumblrImagesScraper:
    def __init__(self):

        self.proxies = None

    async def _get_response(self, session, url):
        if self.proxies:
            for _ in range(len(self.proxies)):
                try:
                    proxy = random.choice(self.proxies)
                    async with session.get(url, proxy=proxy, timeout=3) as response:
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
            async with session.get(url) as response:
                assert response.status == 200, "Could not connect. Check your internet connection"
                return await response.read()

    async def _save_image(self, session, url, path):
        if self.proxies:
            for _ in range(len(self.proxies) + 1):
                try:
                    proxy = random.choice(self.proxies)
                    async with session.get(url, proxy=proxy, timeout=3) as resp:
                        if resp.status == 200:
                            f = await aiofiles.open(path, mode='wb+')
                            await f.write(await resp.read())
                            await f.close()
                except aiohttp.ClientConnectionError:
                    warnings.warn("Invalid URL recieved. Continuing")
                    return
                except aiohttp.ClientPayloadError:
                    warnings.warn("Encountered Payload error. This is caused due to unacceptable headers. Continuing")
                    return
                except (asyncio.TimeoutError, aiohttp.client.ClientProxyConnectionError,
                        aiohttp.client.ClientHttpProxyError, aiohttp.client.ServerDisconnectedError,
                        aiohttp.client.ClientOSError):
                    try:
                        self.proxies.remove(proxy)
                    except ValueError:
                        pass
                    continue
        else:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        f = await aiofiles.open(path, mode='wb+')
                        await f.write(await resp.read())
                        await f.close()
            except aiohttp.ClientConnectionError:
                warnings.warn("Invalid URL recieved. Continuing")
                return
            except aiohttp.ClientPayloadError:
                warnings.warn("Encountered Payload error. This is caused due to unacceptable headers. Continuing")
                return

    async def _post_request(self, session, query, page, key):
        post_headers = {'authority': 'www.tumblr.com', 'method': 'POST', 'scheme': 'https',
                             'accept': 'application/json, text/javascript, */*; q=0.01',
                             'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9',
                             'cache-control': 'no-cache',
                             'content-type': 'application/x-www-form-urlencoded; charset=UTF-8', 'dnt': '1',
                             'origin': 'https://www.tumblr.com', 'pragma': 'no-cache', 'sec-fetch-dest': 'empty',
                             'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin',
                             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36',
                             'x-requested-with': 'XMLHttpRequest', 'referer': f'https://www.tumblr.com/search/{query}',
                             'path': f'/search/{query}/post_page/{page}', 'x-tumblr-form-key': key}
        data = {'q': query,
                'sort': 'top', 'post_view': 'masonry',
                'blogs_before': '11',
                'num_blogs_shown': '8',
                'num_posts_shown': 20 + 40 * (page - 2), 'before': 22 + 45 * (page - 1),
                'blog_page': '2', 'safe_mode': True,
                'post_page': page, 'filter_nsfw': True,
                'next_ad_offset': '0',
                'ad_placement_id': '0',
                'more_posts': True}
        if self.proxies:
            for _ in range(len(self.proxies)):
                try:
                    proxy = random.choice(self.proxies)
                    resp = await session.post(f'https://www.tumblr.com/search/{query}/post_page/{page}', data=data,
                                  headers=post_headers, proxy=proxy, timeout=3)
                    return await resp.read()
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
            resp = await session.post(f'https://www.tumblr.com/search/{query}/post_page/{page}', data=data,
                                      headers=post_headers)
            return await resp.read()

    async def _parse_json(self, session, json_contents, out_path):
        html_content = BeautifulSoup(json_contents['response']['posts_html'], 'lxml')
        all_images = html_content.findAll('img', {'class': 'post_media_photo'})
        coros = [self._save_image(session, img['src'],
                                  os.path.join(out_path, f'{uuid.uuid1()}.jpg') if out_path else f'{uuid.uuid1()}.jpg')
                 for img in all_images]
        await asyncio.gather(*coros)

    async def _main_exec(self, query, num_pages, out_path=None):
        async with aiohttp.ClientSession() as session:
            try:
                resp = await self._get_response(session, f'https://www.tumblr.com/search/{query}')
            except Exception:
                raise
            bs4_page = BeautifulSoup(resp, 'lxml')
            key = bs4_page.find('meta', {"name": "tumblr-form-key"})['content']

            all_images = bs4_page.findAll('img', {'class': 'post_media_photo'})
            coros = [self._save_image(session, img['src'], os.path.join(out_path,
                                                                        f'{uuid.uuid1()}.jpg') if out_path else f'{uuid.uuid1()}.jpg')
                     for img in all_images]
            await asyncio.gather(*coros)

            if num_pages > 1:
                try:
                    coros = [self._post_request(session, query, page, key) for page in range(2, num_pages + 1, 1)]
                except Exception:
                    raise
                responses = await asyncio.gather(*coros)

                json_responses = [json.loads(resp.decode()) for resp in responses]
                coros = [self._parse_json(session, response, out_path) for response in json_responses]
                await asyncio.gather(*coros)

        print(f"Finished scraping {num_pages} pages to {out_path}")

    def scrape(self, query, num_pages, out_path=None, proxies=None):
        '''
        query: str, Search term for GIPHY
        num_pages: int, Number of GIFs to scrape
        out_path: str, Path to output directory
        proxies: list, list of HTTP/Upgradable HTTPS proxies. These proxies are automatically rotated
        '''
        assert query != '' and type(query) is str, "Invalid query"
        if out_path:
            assert os.path.isdir(out_path), "Invalid output directory"
        if proxies:
            assert proxies is not None, "Invalid proxies received"
            self.proxies = proxies
        assert num_pages >= 1, "Number of pages cannot be zero or negative"

        query = query.replace(' ', '+')

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._main_exec(query, num_pages, out_path))
        loop.close()
