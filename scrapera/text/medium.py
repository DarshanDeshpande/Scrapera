import asyncio
import os
import random
import aiohttp
import aiosqlite
import pprint


class MediumScraper:
    """
    Scrapper for Medium Article Scraper
    """

    def __init__(self):
        self.proxies = None

        self.post_headers = {
            'Content-Type': 'application/json',
        }

        self.url = "https://medium.com/_/graphql"

    async def _post_response(self, session, n_posts, topic=None):
        global_post_data = {
            "operationName": "WebRankedModulesScreen",
            "variables": {},
            "query": "query WebRankedModulesScreen {"
                     "\n  webRankedModules("
                     "\n    options: {recommendationSurface: MODULAR_WEB_HP, icelandVersion: ICELAND_GENERAL_RELEASE}"
                     "\n  ) {"
                     "\n    ... on Modules {"
                     "\n      modules {"
                     "\n        ...BasePostModuleData"
                     "\n        ...HomeFeedModuleData"
                     "\n      }"
                     "\n    }"
                     "\n  }"
                     "\n}"
                     "\n"
                     "\nfragment BasePostModuleData on BaseRankedModule {"
                     "\n  entities: items {"
                     "\n    ... on ModuleItemPost {"
                     "\n      post {"
                     "\n        ...PostListModulePostPreviewData"
                     "\n        id"
                     "\n      }"
                     "\n    }"
                     "\n  }"
                     "\n}"
                     "\nfragment PostListModulePostPreviewData on Post{"
                     "\n  id"
                     "\n  mediumUrl"
                     "\n  title"
                     "\n  creator {"
                     "\n     name"
                     "\n}"
                     "\n}"
                     "\nfragment HomeFeedModuleData on ExtendedFeedRankedModule {"
                     "\n  feedItems {"
                     "\n    post {"
                     "\n      ...PostListModulePostPreviewData"
                     "\n    }"
                     "\n    postId"
                     "\n  }"
                     "\n  extendedFeedItems {"
                     "\n    postId"
                     "\n  }"
                     "\n}"
        }
        topic_post_data = {
            "operationName": "TopicHandler",
            "variables": {
                "topicSlug": "",
                "feedPagingOptions": {
                    "limit": 25,
                    "to": ""
                },

            },
            "query": "query TopicHandler($topicSlug: ID!, $feedPagingOptions: PagingOptions) {"
                     "\n     topic(slug: $topicSlug) {"
                     "\n       canonicalSlug"
                     "\n       ...TopicScreen_topic"
                     "\n     }"
                     "\n   }"
                     "\n   fragment PostListingItemFeed_postPreview on PostPreview {"
                     "\n     post {"
                     "\n       ...PostListingItemPreview_post"
                     "\n       id"
                     "\n     }"
                     "\n   }"
                     "\n   fragment PostListingItemPreview_post on Post {"
                     "\n     id"
                     "\n     mediumUrl"
                     "\n     title"
                     "\n     creator {"
                     "\n       name"
                     "\n     }"
                     "\n   }"
                     "\n   fragment PostListingItemImage_post on Post {"
                     "\n     id"
                     "\n     mediumUrl"
                     "\n   }"
                     "\n   fragment TopicScreen_topic on Topic {"
                     "\n     id"
                     "\n     ...TopicMetadata_topic"
                     "\n     ...TopicFeaturedAndLatest_topic"
                     "\n     __typename"
                     "\n   }"
                     "\n   fragment TopicMetadata_topic on Topic {"
                     "\n     name"
                     "\n     description"
                     "\n     slug"
                     "\n   }"
                     "\n   fragment TopicFeaturedAndLatest_topic on Topic {"
                     "\n     name"
                     "\n     slug"
                     "\n     featuredPosts {"
                     "\n       postPreviews {"
                     "\n         post {"
                     "\n           id"
                     "\n           ...TopicLandingFeaturedStory_post"
                     "\n         }"
                     "\n       }"
                     "\n     }"
                     "\n     latestPosts(paging: $feedPagingOptions) {"
                     "\n       postPreviews {"
                     "\n         post {"
                     "\n           id"
                     "\n         }"
                     "\n         ...PostListingItemFeed_postPreview"
                     "\n       }"
                     "\n       pagingInfo {"
                     "\n         next {"
                     "\n           limit"
                     "\n           to"
                     "\n         }"
                     "\n       }"
                     "\n     }"
                     "\n     id"
                     "\n   }"
                     "\n   fragment TopicLandingFeaturedStory_post on Post {"
                     "\n     ...FeaturedPostPreview_post"
                     "\n     ...PostListingItemPreview_post"
                     "\n     ...PostListingItemBylineWithAvatar_post"
                     "\n     ...PostListingItemImage_post"
                     "\n     id"
                     "\n   }"
                     "\n   fragment FeaturedPostPreview_post on Post {"
                     "\n     id"
                     "\n     title"
                     "\n     mediumUrl"
                     "\n   }"
                     "\n   fragment PostListingItemBylineWithAvatar_post on Post {"
                     "\n     creator {"
                     "\n         name"
                     "\n     }"
                     "\n     id"
                     "\n  }"
        }
        response_list = []

        if topic is None:
            return await self._post_response_utils(session, global_post_data)
        else:
            post_iter_id = ""
            topic_post_data['variables']['topicSlug'] = topic
            for i in range(n_posts // 25 if n_posts // 25 else 1):
                topic_post_data['variables']['feedPagingOptions']['to'] = post_iter_id
                resp = await self._post_response_utils(session, topic_post_data)
                if resp['data']['topic'] is None:
                    raise AssertionError("Topic is invalid, check the medium website url for exact topic name")
                post_iter_id = resp['data']['topic']['latestPosts']['pagingInfo']['next']['to']
                response_list.append(resp)
        return response_list[:n_posts]

    async def _post_response_utils(self, session, data_send):
        if self.proxies:
            for _ in range(len(self.proxies)):
                try:
                    proxy = random.choice(self.proxies)

                    async with session.post(self.url, headers=self.post_headers, json=data_send) as response:
                        assert response.status == 200
                        resp = await response.json()
                        return resp

                except Exception as e:
                    print(e)
                    try:
                        self.proxies.remove(proxy)
                        if not self.proxies:
                            raise AssertionError("Exhausted all proxies. Ensure that your proxies are valid")
                    except ValueError:
                        pass
                    continue
        else:
            async with session.post(self.url, headers=self.post_headers, json=data_send) as response:
                assert response.status == 200
                resp = await response.json()
                return resp

    @staticmethod
    async def extract_post_objects_topic(response_list, n_posts):

        post_objects = []

        for i, resp in enumerate(response_list):
            if i == 0:
                post_objects += resp['data']['topic']['featuredPosts']['postPreviews']
            post_objects += resp['data']['topic']['latestPosts']['postPreviews']
        return post_objects[:n_posts]

    async def extract_post_objects_general(self, session, response, n_posts):
        post_objects = []
        initial_posts = response['data']['webRankedModules']['modules'][1]['entities']
        next_posts = response['data']['webRankedModules']['modules'][2]['feedItems']
        post_items_ids = response['data']['webRankedModules']['modules'][2]['extendedFeedItems']
        extended_data = {
            "operationName": "ExtendedFeedQuery",
            "variables": {
                "items": post_items_ids
            },
            "query": "query ExtendedFeedQuery($items: [ExtendedFeedItemOptions!]!) {"
                     "\n  extendedFeedItems(items: $items) {"
                     "\n    post {"
                     "\n      ...PostListModulePostPreviewData"
                     "\n    }"
                     "\n  }"
                     "\n}"
                     "\nfragment PostListModulePostPreviewData on Post {"
                     "\n  id"
                     "\n  mediumUrl"
                     "\n  title"
                     "\n  creator {"
                     "\n    name"
                     "\n  }"
                     "\n}"
        }

        if len(initial_posts) + len(next_posts) < n_posts:
            async with session.post(self.url, headers=self.post_headers, json=extended_data) as response1:
                assert response1.status == 200

                resp_json1 = await response1.json()
                post_items_objs = resp_json1['data']['extendedFeedItems']

                post_objects += initial_posts + next_posts + post_items_objs

                if len(post_objects) < n_posts:
                    raise ValueError(f"Posts exhausted, available number of top articles is {len(post_objects)}")
        else:
            post_objects += initial_posts + next_posts

        return post_objects[:n_posts]

    async def get_page_content(self, session, post):
        pid = post['post']['id']
        link = post['post']['mediumUrl']
        author = post['post']['creator']['name']

        content_graphql = {
            "operationName": "PostViewerEdgeContent",
            "variables": {
                "postId": f"{pid}",
                "postMeteringOptions": {
                    "referrer": ""
                }
            },
            "query": "query PostViewerEdgeContent($postId: ID!, $postMeteringOptions: PostMeteringOptions) {"
                     "\n     post(id: $postId) {"
                     "\n       ... on Post {"
                     "\n         id"
                     "\n         viewerEdge {"
                     "\n           id"
                     "\n           fullContent(postMeteringOptions: $postMeteringOptions) {"
                     "\n             bodyModel {"
                     "\n               ...PostBody_bodyModel"
                     "\n             }"
                     "\n           }"
                     "\n         }"
                     "\n       }"
                     "\n     }"
                     "\n   }"
                     "\n   fragment PostBody_bodyModel on RichText {"
                     "\n     paragraphs {"
                     "\n       id"
                     "\n       ...PostBodySection_paragraph"
                     "\n       __typename"
                     "\n     }"
                     "\n     ...normalizedBodyModel_richText"
                     "\n     __typename"
                     "\n   }"
                     "\n   fragment normalizedBodyModel_richText on RichText {"
                     "\n     paragraphs {"
                     "\n       markups {"
                     "\n         type"
                     "\n         __typename"
                     "\n       }"
                     "\n       ...getParagraphHighlights_paragraph"
                     "\n       ...getParagraphPrivateNotes_paragraph"
                     "\n       __typename"
                     "\n     }"
                     "\n     sections {"
                     "\n       startIndex"
                     "\n       ...getSectionEndIndex_section"
                     "\n       __typename"
                     "\n     }"
                     "\n     ...getParagraphStyles_richText"
                     "\n     ...getParagraphSpaces_richText"
                     "\n     __typename"
                     "\n   }"
                     "\n   fragment getParagraphHighlights_paragraph on Paragraph {"
                     "\n     name"
                     "\n     __typename"
                     "\n     id"
                     "\n   }"
                     "\n   fragment getParagraphPrivateNotes_paragraph on Paragraph {"
                     "\n     name"
                     "\n     __typename"
                     "\n     id"
                     "\n   }"
                     "\n   fragment getSectionEndIndex_section on Section {"
                     "\n     startIndex"
                     "\n     __typename"
                     "\n   }"
                     "\n   fragment getParagraphStyles_richText on RichText {"
                     "\n     paragraphs {"
                     "\n       text"
                     "\n       type"
                     "\n       __typename"
                     "\n     }"
                     "\n     sections {"
                     "\n       ...getSectionEndIndex_section"
                     "\n       __typename"
                     "\n     }"
                     "\n     __typename"
                     "\n   }"
                     "\n   fragment getParagraphSpaces_richText on RichText {"
                     "\n     paragraphs {"
                     "\n       layout"
                     "\n       metadata {"
                     "\n         originalHeight"
                     "\n         originalWidth"
                     "\n         __typename"
                     "\n       }"
                     "\n       type"
                     "\n       ...paragraphExtendsImageGrid_paragraph"
                     "\n       __typename"
                     "\n     }"
                     "\n     ...getSeriesParagraphTopSpacings_richText"
                     "\n     ...getPostParagraphTopSpacings_richText"
                     "\n     __typename"
                     "\n   }"
                     "\n   fragment paragraphExtendsImageGrid_paragraph on Paragraph {"
                     "\n     layout"
                     "\n     type"
                     "\n     __typename"
                     "\n     id"
                     "\n   }"
                     "\n   fragment getSeriesParagraphTopSpacings_richText on RichText {"
                     "\n     paragraphs {"
                     "\n       id"
                     "\n       __typename"
                     "\n     }"
                     "\n     sections {"
                     "\n       startIndex"
                     "\n       __typename"
                     "\n     }"
                     "\n     __typename"
                     "\n   }"
                     "\n   fragment getPostParagraphTopSpacings_richText on RichText {"
                     "\n     paragraphs {"
                     "\n       layout"
                     "\n       text"
                     "\n       __typename"
                     "\n     }"
                     "\n     sections {"
                     "\n       startIndex"
                     "\n       __typename"
                     "\n     }"
                     "\n     __typename"
                     "\n   }"
                     "\n   fragment PostBodySection_paragraph on Paragraph {"
                     "\n     name"
                     "\n     ...PostBodyParagraph_paragraph"
                     "\n     __typename"
                     "\n     id"
                     "\n   }"
                     "\n   fragment PostBodyParagraph_paragraph on Paragraph {"
                     "\n     name"
                     "\n     type"
                     "\n     ...ImageParagraph_paragraph"
                     "\n     ...TextParagraph_paragraph"
                     "\n     ...IframeParagraph_paragraph"
                     "\n     ...MixtapeParagraph_paragraph"
                     "\n     __typename"
                     "\n     id"
                     "\n   }"
                     "\n   fragment IframeParagraph_paragraph on Paragraph {"
                     "\n     iframe {"
                     "\n       mediaResource {"
                     "\n         id"
                     "\n         iframeSrc"
                     "\n         iframeHeight"
                     "\n         iframeWidth"
                     "\n         title"
                     "\n         __typename"
                     "\n       }"
                     "\n       __typename"
                     "\n     }"
                     "\n     layout"
                     "\n     ...getEmbedlyCardUrlParams_paragraph"
                     "\n     ...Markups_paragraph"
                     "\n     __typename"
                     "\n     id"
                     "\n   }"
                     "\n   fragment getEmbedlyCardUrlParams_paragraph on Paragraph {"
                     "\n     type"
                     "\n     iframe {"
                     "\n       mediaResource {"
                     "\n         iframeSrc"
                     "\n         __typename"
                     "\n       }"
                     "\n       __typename"
                     "\n     }"
                     "\n     __typename"
                     "\n     id"
                     "\n   }"
                     "\n   fragment Markups_paragraph on Paragraph {"
                     "\n     name"
                     "\n     text"
                     "\n     hasDropCap"
                     "\n     dropCapImage {"
                     "\n       ...MarkupNode_data_dropCapImage"
                     "\n       __typename"
                     "\n       id"
                     "\n     }"
                     "\n     markups {"
                     "\n       type"
                     "\n       start"
                     "\n       end"
                     "\n       href"
                     "\n       anchorType"
                     "\n       userId"
                     "\n       linkMetadata {"
                     "\n         httpStatus"
                     "\n         __typename"
                     "\n       }"
                     "\n       __typename"
                     "\n     }"
                     "\n     __typename"
                     "\n     id"
                     "\n   }"
                     "\n   fragment MarkupNode_data_dropCapImage on ImageMetadata {"
                     "\n     ...DropCap_image"
                     "\n     __typename"
                     "\n     id"
                     "\n   }"
                     "\n   fragment DropCap_image on ImageMetadata {"
                     "\n     id"
                     "\n     originalHeight"
                     "\n     originalWidth"
                     "\n     __typename"
                     "\n   }"
                     "\n   fragment ImageParagraph_paragraph on Paragraph {"
                     "\n     href"
                     "\n     layout"
                     "\n     metadata {"
                     "\n       id"
                     "\n       originalHeight"
                     "\n       originalWidth"
                     "\n       focusPercentX"
                     "\n       focusPercentY"
                     "\n       alt"
                     "\n       __typename"
                     "\n     }"
                     "\n     ...Markups_paragraph"
                     "\n     ...ParagraphRefsMapContext_paragraph"
                     "\n     ...PostAnnotationsMarker_paragraph"
                     "\n     __typename"
                     "\n     id"
                     "\n   }"
                     "\n   fragment ParagraphRefsMapContext_paragraph on Paragraph {"
                     "\n     id"
                     "\n     name"
                     "\n     text"
                     "\n     __typename"
                     "\n   }"
                     "\n   fragment PostAnnotationsMarker_paragraph on Paragraph {"
                     "\n     ...PostViewNoteCard_paragraph"
                     "\n     __typename"
                     "\n     id"
                     "\n   }"
                     "\n   fragment PostViewNoteCard_paragraph on Paragraph {"
                     "\n     name"
                     "\n     __typename"
                     "\n     id"
                     "\n   }"
                     "\n   fragment TextParagraph_paragraph on Paragraph {"
                     "\n     type"
                     "\n     hasDropCap"
                     "\n     ...Markups_paragraph"
                     "\n     ...ParagraphRefsMapContext_paragraph"
                     "\n     __typename"
                     "\n     id"
                     "\n   }"
                     "\n   fragment MixtapeParagraph_paragraph on Paragraph {"
                     "\n     text"
                     "\n     type"
                     "\n     mixtapeMetadata {"
                     "\n       href"
                     "\n       thumbnailImageId"
                     "\n       __typename"
                     "\n     }"
                     "\n     markups {"
                     "\n       start"
                     "\n       end"
                     "\n       type"
                     "\n       href"
                     "\n       __typename"
                     "\n     }"
                     "\n     __typename"
                     "\n     id"
                     "\n   }"
        }

        full_text = ""
        try:
            async with session.post(self.url, headers=self.post_headers, json=content_graphql) as response:
                assert response.status == 200
                resp = await response.json()
                paragraphs = resp['data']['post']['viewerEdge']['fullContent']['bodyModel']['paragraphs']
                for paragraph in paragraphs:
                    full_text += str(paragraph['text']).strip() + "\n"
        except Exception as e:
            print(e)
        return {"text": full_text, "author": author, "link": link}

    @staticmethod
    async def _write_to_db(output_dict, cursor, db):

        await cursor.execute("INSERT OR REPLACE INTO ARTICLES (AUTHOR, LINK, CONTENT) "
                             "VALUES (?,?,?)",
                             (output_dict['author'], output_dict['link'], output_dict['text']))
        await db.commit()

    async def _main_exec(self, n_posts, topic=None, out_path=None):
        async with aiosqlite.connect(out_path) as db:
            cursor = await db.cursor()
            await cursor.execute(
                "CREATE TABLE IF NOT EXISTS ARTICLES (ID INTEGER PRIMARY KEY AUTOINCREMENT, AUTHOR VARCHAR(100), LINK VARCHAR(255), CONTENT TEXT)")

            async with aiohttp.ClientSession() as session:
                try:

                    if topic is None:
                        resp = await self._post_response(session, n_posts=n_posts)
                        resp = await self.extract_post_objects_general(session, response=resp, n_posts=n_posts)

                    else:
                        resp = await self._post_response(session, topic=topic, n_posts=n_posts)
                        resp = await self.extract_post_objects_topic(response_list=resp, n_posts=n_posts)

                    coros = [self.get_page_content(session, post=post) for post in resp]
                    db_objs = await asyncio.gather(*coros)

                    coros = [self._write_to_db(output_dict=post, cursor=cursor, db=db) for post in db_objs]
                    await asyncio.gather(*coros)

                except Exception as e:
                    print(e)

    def scrape(self, n_posts, topic=None, out_path=None, proxies=None):

        """
        n_posts: int, Number of articles to be scraped. General post has 301 posts
        topic: str, topic of the article to be scraped. Check the medium website url for types of topics.
        out_path:  str, Path to output directory
        proxies: list, list of HTTP/Upgradable HTTPS proxies. These proxies are automatically rotated
        """

        assert n_posts >= 1 and type(
            n_posts) is int, "Number of posts cannot be zero or negative"
        if out_path:
            assert os.path.isdir(out_path), "Invalid output directory"
        if proxies:
            assert proxies is not None, "Invalid proxies received"
            self.proxies = proxies

        out_path = os.path.join(out_path, 'MediumArticles.db') if out_path else 'MediumArticles.db'
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._main_exec(topic=topic, n_posts=n_posts, out_path=out_path))
        loop.close()
