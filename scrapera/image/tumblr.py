import json
import os
import urllib.request
import uuid

import brotli
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


class TumblrImagesScraper:
    def __init__(self):
        self.headers = {'authority': 'www.tumblr.com',
                        'method': 'POST',
                        'scheme': 'https',
                        'accept': 'application/json, text/javascript, */*; q=0.01',
                        'accept-encoding': 'gzip, deflate, br',
                        'accept-language': 'en-US,en;q=0.9',
                        'cache-control': 'no-cache',
                        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'dnt': '1',
                        'origin': 'https://www.tumblr.com',
                        'pragma': 'no-cache',
                        'sec-fetch-dest': 'empty',
                        'sec-fetch-mode': 'cors',
                        'sec-fetch-site': 'same-origin',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36',
                        'x-requested-with': 'XMLHttpRequest'}

    def scrape(self, query, num_pages, out_path=None, proxies=None):

        assert query != '', "Invalid query"
        assert num_pages >= 1, "Number of pages cannot be zero or negative"
        if out_path:
            assert os.path.isdir(out_path), "Invalid output path received"

        query = query.replace(' ', '+')

        session = requests.Session()
        session.proxies = proxies
        resp = session.get(f'https://www.tumblr.com/search/{query}')
        bs4_page = BeautifulSoup(resp.content, 'lxml')
        key = bs4_page.find('meta', {"name": "tumblr-form-key"})['content']

        all_images = bs4_page.findAll('img', {'class': 'post_media_photo'})
        for index, img in enumerate(all_images):
            urllib.request.urlretrieve(img['src'], os.path.join(out_path,
                                                                f'{uuid.uuid1()}.jpg') if out_path else f'{uuid.uuid1()}.jpg')
        num_images = len(all_images)
        if num_pages > 1:
            for page in tqdm(range(2, num_pages + 1, 1)):
                self.headers['referer'] = f'https://www.tumblr.com/search/{query}'
                self.headers['path'] = f'/search/{query}/post_page/{page}'
                self.headers['x-tumblr-form-key'] = key

                resp = session.post(f'https://www.tumblr.com/search/{query}/post_page/{page}',
                                    data={'x-tumblr-form-key': key, 'q': {query},
                                          'sort': 'top', 'post_view': 'masonry',
                                          'blogs_before': '11',
                                          'num_blogs_shown': '8',
                                          'num_posts_shown': {20 + 40 * (page - 2)}, 'before': {25 + 40 + page},
                                          'blog_page': '2', 'safe_mode': True,
                                          'post_page': {page}, 'filter_nsfw': True,
                                          'next_ad_offset': '0',
                                          'ad_placement_id': '0',
                                          'more_posts': True}, headers=self.headers)

                json_contents = json.loads(brotli.decompress(resp.content).decode())
                html_content = BeautifulSoup(json_contents['response']['posts_html'], 'lxml')
                all_images = html_content.findAll('img', {'class': 'post_media_photo'})
                for index, img in enumerate(all_images):
                    urllib.request.urlretrieve(img['src'], os.path.join(out_path,
                                                                        f'{uuid.uuid1()}.jpg') if out_path else f'{uuid.uuid1()}.jpg')

            num_images += len(all_images)

        print(f"Finished scraping {num_pages} pages. Saved {num_images} images to {out_path}")
