import csv
import json
import os
import urllib
import urllib.request


class InstagramCommentsScraper:
    '''
    Scraper for Instagram Comments.
    This implementation is broken due to recent GraphQL changes and only around 25 comments can be scraped as of now
    '''

    def _extract_get_comments_data(self, json_response):
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

        return timestamp, texts, usernames

    def scrape(self, url, out_path=None, urllib_proxies=None):
        '''
        Scraper function for scraping comments related to a specific Instagarm post
        url: str, URL for the Instagram post to be scraped
        out_path:  [Optional] str, Path to output directory. If unspecified, current directory will be used
        urllib_proxies:  [Optional] dict, Proxy information for urllib requests
        '''
        data = self._extract_post_json(url, urllib_proxies)

        with open('ScrapedComments.csv' if out_path is None else os.path.join(out_path, 'ScrapedComments.csv'), 'a+',
                  encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(['Timestamp', 'Text', 'Username'])
            for row in zip(*data):
                writer.writerow(row)
