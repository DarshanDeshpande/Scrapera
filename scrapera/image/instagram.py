import json
import os
import time
import urllib
import urllib.request

from PIL import Image


class InstagramImageScraper:
    def _extract_image(self, json_response, out_path=None, resize=None):
        name_of_file = str(json_response['graphql']['shortcode_media']['owner']['username']) + '_' + str(
            json_response['graphql']['shortcode_media']['id'])
        img_link = json_response['graphql']['shortcode_media']['display_resources'][-1]['src']
        path_to_file = os.path.join(f"{out_path}", f"{name_of_file}.jpeg") if out_path else f"{name_of_file}.jpeg"
        start_time = time.time()
        urllib.request.urlretrieve(img_link, path_to_file)
        print(f"Download finished in {(time.time()-start_time):.2f} seconds")
        if resize is not None:
            image = Image.open(path_to_file)
            image.resize(resize).save(path_to_file)

    def _extract_post(self, url, urllib_proxies=None, out_path=None, resize=None):
        url = f"https://www.instagram.com/p/{url.split('/')[-2]}/?__a=1"

        req = urllib.request.Request(url, None, {"User-Agent": "Mozilla/5.0"})

        if urllib_proxies:
            handler = urllib.request.ProxyHandler(urllib_proxies)
            opener = urllib.request.build_opener(handler)
            urllib.request.install_opener(opener)

        response = urllib.request.urlopen(req)
        json_response = json.load(response)

        self._extract_image(json_response, out_path, resize)

    def scrape(self, url, out_path=None, resize=None, urllib_proxies=None):
        '''
        url: str, URL for the Instagram post to be scraped
        out_path:  [Optional] str, Path to output directory. If unspecified, current directory will be used
        resize: [Optional] tuple or list, None or tuple of shape (new_width, new_height)
        urllib_proxies:  [Optional] dict, Proxy information for urllib requests
        '''
        if urllib_proxies:
            assert type(urllib_proxies) is dict, "Input to 'urllib_proxies' should be a dictionary"
        if out_path:
            assert os.path.isdir(out_path), "Invalid output directory"
        assert type(resize) in [list, tuple, set] and len(
            resize) == 2, "'resize' parameter should be an iterable and should be of the form (new_width, new_height)"
        self._extract_post(url, urllib_proxies, out_path, resize)
