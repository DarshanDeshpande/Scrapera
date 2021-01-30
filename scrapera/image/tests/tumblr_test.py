from scrapera.image.tumblr import TumblrImagesScraper

scraper = TumblrImagesScraper()
scraper.scrape('dogs', 5, r'path/to/output/directory')
