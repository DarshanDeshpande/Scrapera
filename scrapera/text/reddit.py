import os
import time
import json
import random
import urllib
import urllib.request
from urllib.error import URLError, HTTPError


class RedditPostScraper:
    '''
    Scraper for Reddit posts and comments based on a search string
    '''
    def __init__(self):
        self.last_post_id = 0
        self.posts_data = {}
        self.conn_error = False
        self.data_exhausted = False
        self.topic = ""
        self.post_count = 0

        self.search_url = "https://gateway.reddit.com/desktopapi/v1/search?q={}"
        self.comments_url = "https://gateway.reddit.com/desktopapi/v1/postcomments/{}"

    def _get_comments(self, id):
        comments_data = {}
        req = urllib.request.Request(self.comments_url.format(id), None, {"User-Agent": "Mozilla/5.0"})
        try:
            response = urllib.request.urlopen(req)
        except Exception as e:
            print(e)
            return {}
        comments_extracted = json.load(response).get('comments')
        for commentId in comments_extracted:
            authorId = comments_extracted[commentId].get('authorId')
            text = comments_extracted[commentId].get('bodyMD')
            if authorId and text:
                comments_data[commentId] = {'author': comments_extracted[commentId]['author'], 'text': text, 
                    'upVotes': comments_extracted[commentId]['score']}
        return comments_data


    def _get_json(self):
        req = urllib.request.Request(self.search_url.format(self.topic, self.last_post_id), None,
                                     {"User-Agent": "Mozilla/5.0"})
        try:
            time.sleep(random.randint(0, 1))
            response = urllib.request.urlopen(req)
        except Exception:
            self.conn_error = True
            return False
        comments = {}
        json_data = json.load(response)
        subreddits = json_data['subreddits']
        postIds = list(json_data['posts'].keys())

        if not postIds:
            self.data_exhausted = True
            return None

        for postId in postIds:
            post = json_data['posts'].get(postId)
            if not post:
                continue
            author_id = post['belongsTo']['id']
            if post['belongsTo']['type'] == 'subreddit':
                subreddit = subreddits.get(author_id)['displayText']
            else:
                subreddit = f'u/{post["author"]}'
            if self.comments_flag:
                comments = self._get_comments(postId)
            comments = self._get_comments(postId)
            self.posts_data[postId] = {'title': post.get("title"), 'numComments': post.get("numComments"),
                                         'upVotes': post.get("score"), 'author': post.get("author"),
                                         'subreddit': subreddit, 'isSponsored': post.get('isSponsored'),
                                         'link': post.get("permalink"), 'comments': comments}
            self.post_count += 1
        self.last_post_id = postIds[-1]

    def scrape(self, topic="", numposts=100, comments=False, sleepinterval=None, out_path=None, urllib_proxies=None):
        '''
        topic: str, topic to search reddit
        numposts: [Optional] int, maximum number of posts to scrape
        comments: [Optional] bool, flag for scraping comments data
        sleepinterval: [Optional] list(int), sleep interval in between requests
        out_path: [Optional] str, Path to output directory. If unspecified, current directory will be used
        urllib_proxies: [Optional] dict, Proxy information for urllib requests
        '''
        if sleepinterval is None:
            sleepinterval = [0, 2]
        if not topic:
            print("Empty topic")
            return False
        assert len(sleepinterval) == 2, 'sleepinterval list must be of length 2'
        self.comments_flag = comments
        self.topic = topic.replace(" ", "+")
        if urllib_proxies:
            handler = urllib.request.ProxyHandler(urllib_proxies)
            opener = urllib.request.build_opener(handler)
            urllib.request.install_opener(opener)
        print('Scraping starts')
        while True:
            if self.post_count >= numposts:
                print(f"Scraped {self.post_count} posts in total")
                break
            elif self.conn_error:
                print("Error in connecting to Reddit")
                break
            elif self.data_exhausted:
                print(f"Found only {self.post_count} posts for given topic, saving scraped data")
                break
            else:
                self._get_json()
                time.sleep(random.randint(*sleepinterval))
        with open("Scraped_reddit_data.json" if out_path is None else os.path.join(out_path, "reddit_data.json"), "w") as f:
            json.dump(self.posts_data, f)
            f.close()
        print("Data saved in reddit_data.json")
