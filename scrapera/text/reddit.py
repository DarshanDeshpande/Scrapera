import os
import json
import random
import aiohttp
import asyncio


class RedditPostScraper:
    '''
    Scraper for Reddit posts and comments based on a search string
    '''
    def __init__(self):
        self.topic = ""
        self.last_post_id = 0
        self.comments_flag = False
        self.posts_data = {}
        self.conn_error = False
        self.data_exhausted = False
        self.post_count = 0
        self.proxies = []
        self.get_headers = {
            "host": "gateway.reddit.com",
            "accept": "application/json, text/html",
            "accept-encoding": "gzip, deflate, br",
            "connection": "keep-alive",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
            }
        self.search_url = "https://gateway.reddit.com/desktopapi/v1/search?q={}&after={}"
        self.comments_url = "https://gateway.reddit.com/desktopapi/v1/postcomments/{}"


    async def _fetch_response(self, session, url):
        """
        Returns JSON response fetched from passed session and URL
        """
        if self.proxies:
            while True:
                if not self.proxies:
                    print("[INFO]: All proxies expired, continuing with current machine IP")
                    break
                proxy = random.choice(self.proxies) if self.proxies else None
                try:
                    async with session.get(url, headers=self.get_headers, proxy=proxy, timeout=3) as response:
                        json_data = await response.json()
                        return json_data
                except (
                            asyncio.TimeoutError, aiohttp.client.ClientProxyConnectionError,
                            aiohttp.client.ClientHttpProxyError,
                            aiohttp.client.ServerDisconnectedError, aiohttp.client.ClientOSError):
                    self.proxies.remove(proxy)

        else:
            async with session.get(url, headers=self.get_headers) as response:
                json_data = await response.json()
                return json_data

    async def _get_comments(self, id):
        """
        Returns comments for a post ID
        """
        comments_data = {}
        async with aiohttp.ClientSession() as session:
            comments_extracted = await self._fetch_response(session, self.comments_url.format(id))
            for commentId, commentBody in comments_extracted.get('comments').items():
                authorId, text = [commentBody.get('authorId'), commentBody.get('bodyMD')] if commentBody else [None, None]
                if authorId and text:
                    comments_data[commentId] = {'author': commentBody.get('author'), 'text': text, 
                        'upVotes': commentBody.get('score')}
        return comments_data


    async def _get_next_page(self):
        """
        Loads next page and calls _get_comments() to get the comments for each post
        """
        async with aiohttp.ClientSession() as session:
            json_data = await self._fetch_response(session, self.search_url.format(self.topic, self.last_post_id))
            if json_data:
                if 'subreddits' in json_data:
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
                        subreddit = subreddits.get(author_id)['displayText'] if post['belongsTo']['type'] == 'subreddit' else f'u/{post["author"]}'
                        comments = await self._get_comments(postId) if self.comments_flag else {}
                        self.posts_data[postId] = {'title': post.get("title"), 'numComments': post.get("numComments"),
                                                    'upVotes': post.get("score"), 'author': post.get("author"),
                                                    'subreddit': subreddit, 'isSponsored': post.get('isSponsored'),
                                                    'link': post.get("permalink"), 'comments': comments}
                        self.post_count += 1
                    self.last_post_id = postIds[-1]

    async def _make_requests(self, numposts=100, out_path=None):
        """
        controls entire process of requesting new pages and handle other critical functionality
        dumps data to json
        """
        print(f"[INFO]: Limit: {numposts} posts\n[INFO]: Scrape comments: {self.comments_flag}")
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
                await self._get_next_page()
        out_path = "Scraped_reddit_data.json" if out_path is None else os.path.join(out_path, "Scraped_reddit_data.json")
        with open(out_path, "w") as f:
            json.dump(self.posts_data, f)
            f.close()
        print(f"[INFO]: Data saved in {out_path}")

    def scrape(self, topic, out_path, numposts=100, comments=False, proxies=None):
        """
        topic: str, topic to search reddit
        out_path: str, Absolute path to output directory
        numposts: [Optional] int, maximum number of posts to scrape
        comments: [Optional] bool, flag for scraping comments data
        proxies: [Optional] dict, Proxy information for urllib requests
        """
        if proxies is None:
            proxies = []
        if not topic:
            print("Empty topic")
            return False
        assert os.path.exists(out_path), f'{out_path} does not exist'
        assert type(proxies) is list, 'Pass proxies as a list of strictly http URLS'
        self.proxies = proxies
        self.comments_flag = comments
        self.topic = topic.replace(" ", "+")
        print('[INFO]: Scraping starts')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._make_requests(numposts, out_path))
        loop.close()
