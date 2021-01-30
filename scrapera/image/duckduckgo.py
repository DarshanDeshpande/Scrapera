import json
import os
import re
import urllib.parse
import urllib.request
import uuid

from bs4 import BeautifulSoup
from tqdm import tqdm


class DuckDuckGoScraper:
    '''
    DuckDuckGo based scraper for images
    '''
    def __init__(self):
        self.headers = {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,"
                                  "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                        "upgrade-insecure-requests": "1",
                        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36"}

    def scrape(self, query, num_pages=1, out_path=None, proxies=None):
        '''
        query: str, Search query for scraping images
        num_pages: int, Number of pages to scrape
        out_path: str, Path to output directory
        proxies: str, HTTP/HTTPS proxies
        '''
        assert os.path.isdir(out_path), "Invalid output directory"
        assert query, "Invalid query"
        assert num_pages >= 1, "Number of pages cannot be negative"

        query = query.replace(' ', '+')

        if proxies:
            handler = urllib.request.ProxyHandler(proxies)
            opener = urllib.request.build_opener(handler)
            urllib.request.install_opener(opener)

        opener = urllib.request.build_opener()
        opener.addheaders = [(i, self.headers[i]) for i in self.headers.keys()]
        urllib.request.install_opener(opener)

        vqd = None
        url = f'https://duckduckgo.com/?' + urllib.parse.urlencode(
            {'q': query, 'iax': 'images', 'iar': 'images', 'ia': 'images'})

        resp = urllib.request.urlopen(url).read()
        all_scripts = BeautifulSoup(resp, 'lxml').findAll('script')
        scripts = [i for i in all_scripts if 'src' not in i.attrs.keys()]
        for script in scripts:
            vqd = re.findall(r"vqd='([0-9]+(-[0-9]+)+)'", ''.join(script.contents))[0][0]
            if vqd:
                break

        if not vqd:
            raise ValueError("Could not find encryption key")

        for page in range(num_pages):

            search_url = f'https://duckduckgo.com/i.js?' + urllib.parse.urlencode({'q': query, 'o': 'json', 'p': page,
                                                                                   's': '100', 'u': 'bing', 'f': ',,,',
                                                                                   'l': 'us-en', 'vqd': vqd})
            resp = urllib.request.urlopen(search_url).read()
            json_contents = json.loads(resp)

            for result in tqdm(json_contents['results']):
                image_path = result['image'].split('/')[-1]
                if image_path.split('.')[-1] in ['jpg', 'png', 'jpeg']:
                    path = os.path.join(out_path, image_path) if out_path else image_path
                else:
                    path = os.path.join(out_path, f'{uuid.uuid1()}.jpg') if out_path else f'{uuid.uuid1()}.jpg'
                try:
                    urllib.request.urlretrieve(result['image'], path)
                except Exception as e:
                    print(f"Could not get image due to {e}")
                    continue

