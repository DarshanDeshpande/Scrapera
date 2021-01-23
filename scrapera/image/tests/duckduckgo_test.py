from scrapera.image.duckduckgo import DuckDuckGoScraper

scraper = DuckDuckGoScraper(r'path/to/chromedriver.exe')
scraper.scrape('spongebob squarepants', 5, r'test_download_dir')
