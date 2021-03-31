from scrapera.text.walmart import WalmartReviewsScraper

scraper = WalmartReviewsScraper()
scraper.scrape(query='tshirt', num_product_pages=1, num_review_pages=1, sleep=0, rotate_agents=True,
               out_path='/path/to/output/directory', proxies=None)
