from scrapera.text.amazon import AmazonReviewScraper

scraper = AmazonReviewScraper()
scraper.scrape(query='smartphone', num_product_pages=5, num_review_pages=3, out_path='path/to/output/directory', sleep=3)
