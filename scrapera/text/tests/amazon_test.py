from scrapera.text.amazon import AmazonReviewScraper

scraper = AmazonReviewScraper(r'path/to/chromedriver.exe', None)
scraper.scrape('smartphone', 1, 10)
