import asyncio
import json
import os
import random
import re
import urllib.parse
import uuid
import warnings
import aiofiles
import aiohttp
from bs4 import BeautifulSoup


class DuckDuckGoScraper:
    def __init__(self):
        self.headers = {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,"
                                  "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                        "upgrade-insecure-requests": "1",
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"}
        self.proxies = None

    async def _get_response(self, session, url):
        if self.proxies:
            for _ in range(len(self.proxies)):
                try:
                    proxy = random.choice(self.proxies)
                    async with session.get(url, headers=self.headers, proxy=proxy, timeout=3) as response:
                        assert response.status == 200
                        return await response.read()
                except (asyncio.TimeoutError, aiohttp.client.ClientProxyConnectionError,
                        aiohttp.client.ClientHttpProxyError, aiohttp.client.ServerDisconnectedError,
                        aiohttp.client.ClientOSError):
                    try:
                        self.proxies.remove(proxy)
                        if not self.proxies:
                            raise AssertionError("Exhausted all proxies. Check if your proxies are working")
                    except ValueError:
                        pass
                    continue
        else:
            async with session.get(url, headers=self.headers) as response:
                assert response.status == 200, "Could not connect. Check your internet connection"
                return await response.read()

    async def _save_image(self, session, url, path):
        if self.proxies:
            for _ in range(len(self.proxies) + 1):
                try:
                    proxy = random.choice(self.proxies)
                    async with session.get(url, headers=self.headers, proxy=proxy, timeout=3) as resp:
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
                async with session.get(url, headers=self.headers) as resp:
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

    async def _get_vqd(self, session, query):
        url = 'https://duckduckgo.com/?' + urllib.parse.urlencode(
            {'q': query, 'iax': 'images', 'iar': 'images', 'ia': 'images'})

        html = await self._get_response(session, url)
        all_scripts = BeautifulSoup(html, 'lxml').findAll('script')
        scripts = [i for i in all_scripts if 'src' not in i.attrs.keys()]
        for script in scripts:
            vqd = re.findall(r"vqd='([0-9]+(-[0-9]+)+)'", ''.join(script.contents))[0][0]
            if vqd:
                break

        if not vqd:
            raise ValueError("Could not find encryption key")
        return vqd

    async def _get_json(self, session, query, page, vqd):
        search_url = 'https://duckduckgo.com/i.js?' + urllib.parse.urlencode({'q': query, 'o': 'json',
                                                                               'p': page + 1, 's': page * 100,
                                                                               'u': 'bing', 'f': ',,,',
                                                                               'l': 'us-en', 'vqd': vqd})
        resp = await self._get_response(session, search_url)
        json_contents = json.loads(resp)
        image_links = set()
        for result in json_contents['results']:
            image_links.add(result['image'])

        return list(image_links)

    async def _main_exec(self, query, num_pages, out_path):
        async with aiohttp.ClientSession() as session:
            vqd = await self._get_vqd(session, query)
            assert vqd is not None, ""
            coros = [self._get_json(session, query, page, vqd) for page in range(num_pages)]
            links = await asyncio.gather(*coros)
            flattened_list = set(sum(links, []))
            coros = [self._save_image(session, url, os.path.join(out_path,
                                                                 f'{uuid.uuid1()}.jpg') if out_path else f'{uuid.uuid1()}.jpg')
                     for url in flattened_list]
            await asyncio.gather(*coros)

    def scrape(self, query, num_pages, out_path=None, proxies=None):
        '''
        query: str, Query for which images are to be fetched
        num_pages: int, Number of pages of images to be scraped. Each page has about 100 images
        out_path: str, Path to output directory
        proxies: list, list of HTTP/Upgradable HTTPS proxies. These proxies are automatically rotated
        '''

        assert num_pages >= 1 and type(
            num_pages) is int, "Number of pages must be a non negative, non zero integer value"
        if out_path:
            assert os.path.isdir(out_path), "Invalid output directory"
        if proxies:
            assert type(proxies) is list or type(proxies) is tuple, "'proxies' must be a list"
            self.proxies = proxies
        query = query.replace(' ', '+')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._main_exec(query, num_pages, out_path))
        loop.close()
