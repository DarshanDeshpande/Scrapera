import json
import os
import re
import time
import urllib.request


class VimeoScraper:
    '''
    Scraping Vimeo videos
    Args:
        out_path:  [Optional] str, Path to output directory. If unspecified, current directory will be used
    '''

    def __init__(self, out_path=None):
        if out_path is not None:
            assert os.path.isdir(out_path), "Invalid output directory"
        self.out_path = out_path

    def scrape(self, url, quality, proxies=None):
        '''
        Scraper function for Vimeo
        Args:
            url: URL of vimeo video to be scraped
            quality: Output video resolution
            proxies: dict, A dictionary containing proxy information
        '''
        video_id = url.split('/')[-1]
        quality = quality
        try:
            req = urllib.request.Request(f'https://player.vimeo.com/video/{video_id}/config?default_to_hd=1')
            req.add_header('User-Agent',
                           'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17')
            if proxies:
                handler = urllib.request.ProxyHandler(proxies)
                opener = urllib.request.build_opener(handler)
                urllib.request.install_opener(opener)

            resp = urllib.request.urlopen(req)
            json_contents = json.load(resp)
        except Exception:
            raise ValueError("Invalid video URL")

        title = json_contents['video']['title']
        file_dicts = json_contents['request']['files']['progressive']
        available_res = [d['quality'] for d in file_dicts]
        if quality in available_res:
            for d in file_dicts:
                if d['quality'] == quality:
                    print('-' * 75)
                    print("Starting download")
                    start_time = time.time()
                    title = re.sub(r'''[\W_]+''', '', title)
                    urllib.request.urlretrieve(d['url'],
                                               f"{self.out_path}/{title}-{quality}.mp4" if self.out_path else f"{title}-{quality}.mp4")
                    print(f"Download completed in {round(time.time() - start_time, 2)}s")
                    print('-' * 75)
        else:
            raise ValueError(
                f"{quality} is not available for this video. {','.join(available_res)} resolutions are available")
