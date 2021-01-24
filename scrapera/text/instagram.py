import os

import pandas as pd
import json
import urllib.request
import urllib


class InstagramCommentsScraper:
    @staticmethod
    def _extract_get_comments_data(json_response):
        comments_list, usernames_list, timestamps_list = [], [], []
        for node in json_response['graphql']['shortcode_media']['edge_media_to_parent_comment']['edges']:
            comments_list.append(node['node']['text'].encode('utf-8', 'replace').decode())
            usernames_list.append(node['node']['owner']['username'])
            timestamps_list.append(node['node']['created_at'])

        return comments_list, usernames_list, timestamps_list

    def _extract_post_json(self, url, urllib_proxies=None):
        url = f"https://www.instagram.com/p/{url.split('/')[-2]}/?__a=1"

        req = urllib.request.Request(url, None, {"User-Agent": "Mozilla/5.0"})

        if urllib_proxies:
            handler = urllib.request.ProxyHandler(urllib_proxies)
            opener = urllib.request.build_opener(handler)
            urllib.request.install_opener(opener)

        response = urllib.request.urlopen(req)
        json_response = json.load(response)

        texts, usernames, timestamp = self._extract_get_comments_data(json_response)
        return texts, usernames, timestamp, len(texts)

    def scrape(self, url, out_path=None, urllib_proxies=None):
        '''
        Scraper function for scraping comments related to a specific Instagarm post
        url: str, URL for the Instagram post to be scraped
        out_path:  [Optional] str, Path to output directory. If unspecified, current directory will be used
        urllib_proxies:  [Optional] dict, Proxy information for urllib requests
        '''
        texts, usernames, timestamps, length = self._extract_post_json(url, urllib_proxies)
        df = pd.DataFrame({'text': texts, 'username': usernames, 'timestamp': timestamps})
        df.to_csv('ScrapedComments.csv' if out_path is None else os.path.join(out_path, 'ScrapedComments.csv'),
                  index=False)
