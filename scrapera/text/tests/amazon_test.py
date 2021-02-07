from scrapera.text.amazon import AmazonReviewScraper

scraper = AmazonReviewScraper()
scraper.scrape(query='smartphone', num_product_pages=5, num_review_pages=3, out_path='path/to/output/directory',
               proxies=['http://154.16.202.22:3128', 'http://5.9.139.148:8080', 'http://88.198.50.103:8080'])
