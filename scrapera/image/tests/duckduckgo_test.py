from scrapera.image.duckduckgo import DuckDuckGoScraper

scraper = DuckDuckGoScraper()
scraper.scrape(query='racoon', num_pages=1, out_path='path/to/output/directory',
               proxies=['http://154.16.202.22:3128', 'http://5.9.139.148:8080', 'http://88.198.50.103:8080'])
