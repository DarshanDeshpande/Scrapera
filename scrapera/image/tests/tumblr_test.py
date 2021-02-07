from scrapera.image.tumblr import TumblrImagesScraper

scraper = TumblrImagesScraper()
scraper.scrape('dogs', 5, r'path/to/output/directory',
               proxies=['http://154.16.202.22:3128', 'http://5.9.139.148:8080', 'http://88.198.50.103:8080'])
