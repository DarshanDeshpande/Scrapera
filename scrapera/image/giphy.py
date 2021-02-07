import asyncio
import json
import os
import random
import uuid
import aiofiles
import aiohttp
import math
import warnings


class GiphyScraper:
    def __init__(self):
        self.get_headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"}
        self.gifs_counter = None
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
                            raise AssertionError("Exhausted all proxies. Check if your proxies are working")
                    except ValueError:
                        pass
        else:
            async with session.get(url, headers=self.get_headers) as response:
                assert response.status == 200
                return await response.read()

    async def _save_image(self, session, url, path):
        if self.proxies:
            for _ in range(len(self.proxies) + 1):
                try:
                    proxy = random.choice(self.proxies)
                    async with session.get(url, headers=self.get_headers, proxy=proxy, timeout=3) as resp:
                        if resp.status == 200:
                            f = await aiofiles.open(path, mode='wb+')
                            await f.write(await resp.read())
                            await f.close()
                except aiohttp.ClientConnectionError:
                    warnings.warn("Invalid URL recieved. Continuing")
                    return
                except (asyncio.TimeoutError, aiohttp.client.ClientProxyConnectionError,
                        aiohttp.client.ClientHttpProxyError, aiohttp.client.ServerDisconnectedError,
                        aiohttp.client.ClientOSError):
                    try:
                        self.proxies.remove(proxy)
                        if not self.proxies:
                            raise AssertionError("Exhausted all proxies. Check if your proxies are working")
                    except ValueError:
                        pass
        else:
            async with session.get(url, headers=self.get_headers) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(path, mode='wb+')
                    await f.write(await resp.read())
                    await f.close()

    async def _get_json_data(self, session, json_contents, num_gifs, out_path):
        for data in json_contents['data']:
            if self.gifs_counter < num_gifs + 1:
                image_link = data['images']['original']['url']
                await self._save_image(session, image_link, os.path.join(out_path,
                                                                         f'{uuid.uuid1()}.gif') if out_path else f'{uuid.uuid1()}.gif')
                self.gifs_counter += 1

    async def _get_json(self, session, query, offset):
        try:
            # Alternate Public API key
            # f'https://api.giphy.com/v1/gifs/search?api_key=Gc7131jiJuvI7IdN0HZ1D7nh0ow5BU6g&q={query}&offset={offset}&limit=25'

            resp = await self._get_response(session,
                                            f'https://api.giphy.com/v1/gifs/search?api_key=3eFQvabDx69SMoOemSPiYfh9FY0nzO9x&q={query}&offset={offset}&limit=25')
        except AssertionError:
            raise
        return resp.decode()

    async def _main_exec(self, query, num_gifs, out_path=None):
        offset, flag = 0, False
        self.gifs_counter = 1

        print(f"Fetching results for {query}")
        query = query.replace(' ', '+')

        async with aiohttp.ClientSession() as session:
            # Max 25 GIFs can be fetched at a time
            coros = []
            for i in range(math.ceil(num_gifs / 25)):
                coros.append(self._get_json(session, query, offset))
                offset += 25

            responses = await asyncio.gather(*coros)

            coros = [self._get_json_data(session, json.loads(resp), num_gifs, out_path) for resp in responses]
            await asyncio.gather(*coros)

        print(f"Downloaded {self.gifs_counter - 1} GIFs")

    def scrape(self, query, num_gifs, out_path=None, proxies=None):
        '''
        query: str, Search term for GIPHY
        num_gifs: int, Number of GIFs to scrape
        out_path: str, Path to output directory
        proxies: list, list of HTTP/Upgradable HTTPS proxies. These proxies are automatically rotated
        '''
        assert query != '' and type(query) is str, "Invalid query"
        assert num_gifs >= 1 and type(num_gifs) is int, "Number of GIFs cannot be zero or negative"
        if out_path:
            assert os.path.isdir(out_path), "Invalid output directory"
        if proxies:
            assert proxies and type(proxies) is list, "Invalid proxies received. 'proxies' must be a list"
            self.proxies = proxies

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._main_exec(query, num_gifs, out_path))
        loop.close()
