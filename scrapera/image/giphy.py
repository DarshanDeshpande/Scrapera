import json
import os
import uuid
import urllib.request


class GiphyScraper:
    '''
    GIPHY GIF Scraper
    '''
    def __init__(self):
        self.headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"}

    def scrape(self, query, num_gifs, out_path=None, proxies=None):
        '''
        query: str, Search term for GIPHY
        num_gifs: int, Number of GIFs to scrape
        out_path: str, Path to output directory
        proxies: dict, HTTP/HTTPS proxies
        '''
        assert query != '' and type(query) is str, "Invalid query"
        assert num_gifs >= 1 and type(num_gifs) is int, "Number of GIFs cannot be zero or negative"
        if out_path:
            assert os.path.isdir(out_path), "Invalid output directory"

        if proxies:
            assert type(proxies) is dict, "Invalid proxies received"
            handler = urllib.request.ProxyHandler(proxies)
            opener = urllib.request.build_opener(handler)
            urllib.request.install_opener(opener)

        gifs_counter, offset, flag = 0, 0, False

        print(f"Fetching results for {query}")
        query = query.replace(' ', '+')
        while True:
            # Max 25 GIFs can be fetched at a time
            try:
                req = urllib.request.Request(
                    f'https://api.giphy.com/v1/gifs/search?api_key=3eFQvabDx69SMoOemSPiYfh9FY0nzO9x&q={query}&offset={offset}&limit=25',
                    headers=self.headers)
                resp = urllib.request.urlopen(req).read()
            except Exception:
                # Alternate Public API key
                req = urllib.request.Request(
                    f'https://api.giphy.com/v1/gifs/search?api_key=Gc7131jiJuvI7IdN0HZ1D7nh0ow5BU6g&q={query}&offset={offset}&limit=25',
                    headers=self.headers)
                resp = urllib.request.urlopen(req).read()

            json_contents = json.loads(resp)
            for data in json_contents['data']:
                if gifs_counter < num_gifs:
                    image_link = data['images']['original']['url']
                    urllib.request.urlretrieve(image_link, os.path.join(out_path,
                                                                        f'{uuid.uuid1()}.gif') if out_path else f'{uuid.uuid1()}.gif')
                    gifs_counter += 1
                else:
                    flag = True
                    break

            if flag:
                break

            print(f"{gifs_counter} GIFs downloaded from page {(offset // 25) + 1}")

            offset += 25
        print(f"Downloaded {gifs_counter} GIFs")
