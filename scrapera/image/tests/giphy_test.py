from scrapera.image.giphy import GiphyScraper

scraper = GiphyScraper()
scraper.scrape(query='hello there', num_gifs=20, out_path='path/to/output/directory',
               proxies=['http://154.16.202.22:3128', 'http://5.9.139.148:8080', 'http://88.198.50.103:8080'])
