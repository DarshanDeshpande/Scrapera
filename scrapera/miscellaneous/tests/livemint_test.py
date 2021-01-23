from scrapera.miscellaneous.livemint_stocks import StocksScraper

scraper = StocksScraper(r'path/to/chromedriver.exe')
scraper.scrape(10, "1m")
